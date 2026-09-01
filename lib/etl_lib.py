"""
etl_lib.py

Cleaning, calendar, traceability, OEE, and SPC/AQL helper functions shared
across the notebook Partes 1-2. Centralizing this logic here (instead of copying it
into each notebook) means the *sequence* of decisions stays easy to follow
in the notebooks while the *implementation* stays in one tested place.

Sections:
1. Basic cleaning (whitespace, mixed-case text, disguised "empty" values,
   negative numbers that shouldn't be negative, duplicate rows)
2. Calendar (ISO week, shift)
3. The LotId traceability code
4. OEE calculation
5. SPC / AQL (control limits, Cp/Cpk, DPU/DPMO)
6. Maintenance (planned vs. unplanned downtime)
7. Quality Assurance (customer complaints, suppliers, NC/CAPA)

The raw data (Versão 00, `datasets/bronze/`) is an 18-month, story-driven
dataset built so specific root causes leave a consistent signature across
tables, instead of independent per-row noise -- see
`docs/simulation_storylines.md`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 1. BASIC CLEANING
# ---------------------------------------------------------------------------

# Words that mean "this field has nothing to say" -- a dash, a slash, a
# blank space. pandas doesn't treat these as missing on its own, so a
# maintenance technician named "-" would otherwise show up in a groupby.
BLANK_WORDS = {"-", "--", "---", "/", "//", "\\", "n/a", "na", "none", "null", ""}


def clean_disguised_blanks(df: pd.DataFrame) -> pd.DataFrame:
    """Replaces every BLANK_WORDS token with a real NaN, in every text column."""
    df = df.copy()
    text_columns = df.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        stripped_value = df[column].astype(str).str.strip()
        lowercase_value = stripped_value.str.lower()
        is_blank_word = lowercase_value.isin(BLANK_WORDS)
        df.loc[df[column].notna() & is_blank_word, column] = np.nan
    return df


def strip_extra_spaces(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Trims and collapses whitespace: "  Blow Molding  " -> "Blow Molding"."""
    df = df.copy()
    if columns is None:
        columns = df.select_dtypes(include=["object", "string"]).columns.tolist()

    def fix_text(value):
        if not isinstance(value, str):
            return value
        return " ".join(value.split())

    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(fix_text)
    return df


def standardize_categories(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """'INJECTION MOLDING' / 'injection molding' / 'Injection Molding ' all
    become 'Injection Molding'. .title() is used instead of a lookup table
    so a category no one anticipated still normalizes correctly."""
    df = df.copy()

    def fix_category(value):
        if not isinstance(value, str):
            return value
        return value.strip().title()

    for column in columns:
        if column in df.columns:
            df[column] = df[column].apply(fix_category)
    return df


def fix_negative_quantities(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Some quantity columns show up negative (a sign typo upstream). There's no such thing
    as rejecting -12 pieces, so abs() the value instead of dropping the whole row.

    Scope caveat: this treats every negative value as a sign error, which holds for this
    dataset but not as a universal rule -- in a real industrial system a negative quantity
    can legitimately represent a reversal, return, cancellation, or correction rather than a
    data-entry error, and blindly taking abs() would silently destroy that distinction. A
    real deployment would need to consult the transaction type/reason code before deciding
    abs() is the right fix."""
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = df[column].abs()
    return df


def drop_duplicate_rows(df: pd.DataFrame, columns: list[str] | None = None):
    """Drops exact duplicate rows and reports how many, so nothing
    disappears silently.

    Scope caveat: this only removes byte-for-byte duplicate rows, which is safe here because
    this dataset's duplicates are literal re-emitted records, not two independent events that
    happen to share every field. A real deployment should decide this from the table's actual
    business/event key, since two genuinely distinct events (two readings, two transactions) can
    look like an exact duplicate if the key isn't part of the comparison."""
    rows_before = len(df)
    df = df.drop_duplicates(subset=columns).reset_index(drop=True)
    return df, rows_before - len(df)


def count_missing_values(df: pd.DataFrame) -> pd.Series:
    return df.isna().sum().sort_values(ascending=False)


# ---------------------------------------------------------------------------
# 2. CALENDAR
# ---------------------------------------------------------------------------

def add_calendar_columns(df: pd.DataFrame, date_column: str = "Date") -> pd.DataFrame:
    """Adds ISOWeek and ISOWeekday (1=Monday...7=Sunday). ISO week is used
    (not the plain calendar week) because that's how the plant schedules
    shifts and overtime: a closed Monday-Sunday block, no partial week at
    year boundaries."""
    df = df.copy()
    date = pd.to_datetime(df[date_column])
    iso_calendar = date.dt.isocalendar()
    df["ISOWeek"] = iso_calendar["week"].astype(int)
    df["ISOWeekday"] = iso_calendar["day"].astype(int)
    return df


def compute_shift_number(start_time: pd.Series) -> pd.Series:
    """Shift 1: 06:00-13:59. Shift 2: 14:00-21:59. Shift 3: everything else."""

    def shift_for_one_time(time_value):
        time_value = pd.to_datetime(str(time_value), format="mixed", errors="coerce")
        if pd.isna(time_value):
            return 3
        minutes_of_day = time_value.hour * 60 + time_value.minute
        if 6 * 60 <= minutes_of_day < 14 * 60:
            return 1
        if 14 * 60 <= minutes_of_day < 22 * 60:
            return 2
        return 3

    return start_time.apply(shift_for_one_time).rename("ShiftNumber")


# ---------------------------------------------------------------------------
# 3. LotId TRACEABILITY CODE
# ---------------------------------------------------------------------------

PROCESS_CODE = {
    "Blow Molding": "1",
    "Injection Molding": "2",
    "Screen Printing": "4",
    "Hot Foil Stamping": "5",
}


def machine_number(machine_id: str) -> str:
    """'ISBM-001' -> '01'. MachineId is always LETTERS-NUMBER."""
    parts = str(machine_id).split("-")
    return f"{int(parts[-1]) % 100:02d}"


def work_order_number(work_order: str) -> str:
    """'WO-6005' -> '06005'."""
    parts = str(work_order).split("-")
    return f"{int(parts[-1]) % 100000:05d}"


def build_lotid_prefix(date: pd.Series, shift: pd.Series, process: pd.Series,
                        machine_id: pd.Series, work_order: pd.Series) -> pd.Series:
    """First 14 characters of the LotId: YY WW D T P MM OOOOO
    year(2) + ISO week(2) + ISO weekday(1) + shift(1) + process(1) +
    machine number(2) + work order number(5)."""
    date = pd.to_datetime(date)
    iso_calendar = date.dt.isocalendar()
    year = (date.dt.year % 100).astype(int).astype(str).str.zfill(2)
    week = iso_calendar["week"].astype(int).astype(str).str.zfill(2)
    weekday = iso_calendar["day"].astype(int).astype(str)
    shift_text = shift.astype(int).astype(str)
    process_code = process.map(PROCESS_CODE).fillna("0")
    machine_code = machine_id.apply(machine_number)
    order_code = work_order.apply(work_order_number)
    return year + week + weekday + shift_text + process_code + machine_code + order_code


def compute_material_lot_sequence(consumption: pd.DataFrame, order_column="WorkOrder",
                                   lot_column="MaterialLot",
                                   record_order_column="RecordSeq") -> pd.Series:
    """Last 2 digits of the LotId: starts at 01 per work order, increments
    only when the physical material lot actually changes (not on every
    shift change). A loop is used deliberately -- each row must be compared
    to the row before it in real chronological order, and record_order_column
    guards against the CSV coming back with rows out of order."""
    df = consumption.sort_values([order_column, record_order_column]).copy()
    sequences, counter, previous_order, previous_lot = [], 0, None, None
    for current_order, current_lot in zip(df[order_column], df[lot_column]):
        if current_order != previous_order:
            counter = 1
        elif current_lot != previous_lot:
            counter += 1
        sequences.append(counter)
        previous_order, previous_lot = current_order, current_lot
    result = pd.Series(sequences, index=df.index, name="MaterialLotSeq")
    return result.reindex(consumption.index)


def fill_blank_material_lot(consumption: pd.DataFrame, order_column="WorkOrder",
                             lot_column="MaterialLot",
                             record_order_column="RecordSeq") -> pd.Series:
    """A blank MaterialLot almost always means "operator forgot to write it
    down", not "a new lot started here" -- forward/back-fill it per work
    order so the LotId sequence doesn't come out wrong."""
    df = consumption.sort_values([order_column, record_order_column])
    filled = df.groupby(order_column)[lot_column].transform(lambda s: s.ffill().bfill())
    return filled.reindex(consumption.index)


def compute_end_datetime(date: pd.Series, start_time: pd.Series, end_time: pd.Series,
                          duration_hours: pd.Series | None = None) -> pd.Series:
    """Raw tables only store time-of-day, so an order that runs past
    midnight needs its date rolled forward manually."""
    start_datetime = pd.to_datetime(date) + pd.to_timedelta(start_time.astype(str))
    if duration_hours is not None:
        return start_datetime + pd.to_timedelta(duration_hours.astype(float), unit="h")
    end_time_td = pd.to_timedelta(end_time.astype(str))
    start_time_td = pd.to_timedelta(start_time.astype(str))
    rolled_past_midnight = end_time_td <= start_time_td
    end_datetime = pd.to_datetime(date) + end_time_td
    return end_datetime.where(~rolled_past_midnight, end_datetime + pd.Timedelta(days=1))


def find_work_order_for_stoppage(downtime: pd.DataFrame, production: pd.DataFrame) -> pd.Series:
    """Downtime rows have no WorkOrder of their own; a stoppage is matched
    to whichever order's [start, end) window on that machine contains the
    stoppage moment. When two orders overlap slightly, the one that started
    LAST wins (most recent = actually running). Returns NaN when no order
    was running (e.g. a stoppage logged at the very start of the period,
    or during standalone scheduled maintenance between orders)."""
    stoppage_moment = pd.to_datetime(downtime["Date"]) + pd.to_timedelta(downtime["StoppageStartTime"].astype(str))
    result = pd.Series(np.nan, index=downtime.index, dtype=object)

    for machine in downtime["MachineId"].unique():
        machine_orders = production[production["MachineId"] == machine].sort_values("_start_dt", ascending=False)
        if machine_orders.empty:
            continue
        starts, ends, orders = list(machine_orders["_start_dt"]), list(machine_orders["_end_dt"]), list(machine_orders["WorkOrder"])
        stoppage_indices = downtime[downtime["MachineId"] == machine].index
        for stoppage_index in stoppage_indices:
            time_of_stoppage = stoppage_moment.loc[stoppage_index]
            for start, end, order in zip(starts, ends, orders):
                if start <= time_of_stoppage < end:
                    result.loc[stoppage_index] = order
                    break
    return result


# ---------------------------------------------------------------------------
# 4. OEE CALCULATION
# ---------------------------------------------------------------------------

def compute_oee_components(production: pd.DataFrame, plan: pd.DataFrame,
                            downtime_by_order: pd.DataFrame,
                            capacity_by_machine: dict) -> pd.DataFrame:
    """OEE = Availability x Performance x Quality.
    - Availability = Run Time / Planned Time (Run Time already excludes
      unplanned downtime matched to this work order).
    - Performance = actual pieces/hour vs. the machine's rated pieces/hour,
      capped at 1.0 so OEE stays a proper share of theoretical max output
      (see `PerformanceVsNominal` for the uncapped ratio).
    - Quality = (produced - rejected) / produced.
    """
    df = production.merge(plan[["WorkOrder", "PlannedHours"]], on="WorkOrder", how="left")
    df["PlannedTimeHours"] = df["PlannedHours"].astype(float)

    unplanned_stoppages = downtime_by_order[downtime_by_order["PlannedStoppage"] == "No"]
    setup_stoppages = downtime_by_order[
        downtime_by_order["StoppageReason"].str.contains("Change / Setup|Change/Setup", case=False, na=False, regex=True)
    ]
    unplanned_minutes = unplanned_stoppages.groupby("WorkOrder")["DowntimeDurationMin"].sum()
    setup_minutes = setup_stoppages.groupby("WorkOrder")["DowntimeDurationMin"].sum()

    df["UnplannedDowntimeHours"] = df["WorkOrder"].map(unplanned_minutes).fillna(0) / 60.0
    df["SetupTimeHours"] = df["WorkOrder"].map(setup_minutes).fillna(0) / 60.0

    planned_time = df["PlannedTimeHours"].fillna(df["LeadTimeProdHours"])
    df["RunTimeHours"] = (planned_time - df["UnplannedDowntimeHours"]).clip(lower=0.01)
    df["Availability"] = (df["RunTimeHours"] / df["PlannedTimeHours"]).clip(0, 1)

    rated_capacity = df.apply(lambda row: capacity_by_machine.get((row["MachineId"], row["ToolId"]), np.nan), axis=1)
    df["RatedCapacityPcH"] = rated_capacity
    df["IdealCycleTimeSec"] = 3600.0 / rated_capacity
    # `PerformanceVsNominal` is the RAW ratio, uncapped at 1.0: some orders do run
    # briefly above the machine's nominal rated capacity (up to ~105% in the frozen
    # data), which is a real, worth-showing signal about how RatedCapacityPcH is set
    # -- not noise to hide. But classic OEE is defined as a share of the theoretical
    # maximum good output in the time available, so it cannot exceed 100% by
    # construction; feeding an uncapped (>1) Performance into the OEE product let 52
    # work orders in the frozen dataset show OEE > 100% (max ~104.1%), which breaks
    # that interpretation for every downstream OEE-based comparison. `Performance`
    # (the OEE input) is therefore capped at 1.0, while `PerformanceVsNominal` keeps
    # the uncapped ratio so above-nominal orders remain visible as a distinct signal.
    raw_performance = (df["ProducedQty"] / df["RunTimeHours"]) / rated_capacity
    df["PerformanceVsNominal"] = raw_performance.clip(lower=0)
    df["Performance"] = raw_performance.clip(0, 1)

    df["Quality"] = ((df["ProducedQty"] - df["RejectedQty"]) / df["ProducedQty"]).clip(0, 1)
    df["OEE"] = df["Availability"] * df["Performance"] * df["Quality"]
    df["ActualCycleTimeSec"] = (df["RunTimeHours"] * 3600.0) / df["ProducedQty"]

    df = df.sort_values(["MachineId", "_start_dt"])
    df["_next_start_dt"] = df.groupby("MachineId")["_start_dt"].shift(-1)
    df["ThroughputLeadTimeHours"] = (df["_next_start_dt"] - df["_start_dt"]).dt.total_seconds() / 3600.0
    return df


def compute_production_time(df: pd.DataFrame, start_column="StartTime", end_column="EndTime",
                             duration_hours_column: str | None = None) -> pd.Series:
    if duration_hours_column and duration_hours_column in df.columns:
        return df[duration_hours_column].astype(float)
    start = pd.to_timedelta(df[start_column].astype(str))
    end = pd.to_timedelta(df[end_column].astype(str))
    duration_hours = (end - start).dt.total_seconds() / 3600.0
    duration_hours = np.where(duration_hours < 0, duration_hours + 24, duration_hours)
    return pd.Series(duration_hours, index=df.index, name="LeadTimeProdHours")


UNPLANNED_FAILURE_WORDS = ["Failure", "Shortage", "Unavailable"]


def classify_stoppage(df: pd.DataFrame, reason_column="StoppageReason",
                       planned_column="PlannedStoppage") -> pd.Series:
    """A genuine unplanned FAILURE (breakdown, material shortage) is a
    narrower category than "any unplanned stoppage" (which also includes an
    unplanned mold/tool change)."""
    reason_indicates_failure = df[reason_column].str.contains("|".join(UNPLANNED_FAILURE_WORDS), case=False, na=False)
    was_flagged_unplanned = df[planned_column].str.strip().str.lower().eq("no")
    return reason_indicates_failure & was_flagged_unplanned


SIX_BIG_LOSSES_CATEGORIES = [
    "Quebras (falha não planejada)", "Setup / troca", "Paradas breves / idling",
    "Perda de velocidade", "Perda de qualidade (sucata)",
]


def compute_six_big_losses(production_df: pd.DataFrame, downtime_df: pd.DataFrame,
                            group_columns: list[str] = ("Month", "Process")) -> pd.DataFrame:
    """TPM/Six Big Losses -- the 5 categories measurable with this schema (the 6th,
    startup/yield loss, has no isolating data anywhere in the project). Long format:
    columns `[*group_columns, "LossCategory", "Hours"]`. Pass `group_columns=[]` for a
    single plant-wide total per category instead of a breakdown.

    - Quebras (falha não planejada): downtime where `UnplannedFailure`.
    - Setup / troca: downtime where `IsChangeoverSetup`.
    - Paradas breves / idling: unplanned downtime that is neither a failure nor a
      changeover (e.g. micro-stops) -- `PlannedStoppage == "No"` and neither flag.
    - Perda de velocidade: `RunTimeHours * (1 - Performance)` -- equivalent capacity
      lost to running below rated speed.
    - Perda de qualidade (sucata): `RunTimeHours * Performance * (1 - Quality)` --
      scaled by the SAME Performance already charged to speed loss above, so the same
      run hour isn't counted twice (once as "too slow", again as "made scrap" at full
      nominal speed). `RunTimeHours * (1 - Quality)` alone double-counts with speed
      loss and must not be used -- this is the one and only place in the project that
      is allowed to compute Six Big Losses hours; the gold load and the Parte 4.7
      chart/table both call this function instead of recomputing it inline.
    """
    group_columns = list(group_columns)

    def _hours(df: pd.DataFrame, mask: pd.Series, minutes_column: str) -> pd.DataFrame:
        subset = df.loc[mask]
        if group_columns:
            return (subset.groupby(group_columns)[minutes_column].sum() / 60).rename("Hours").reset_index()
        return pd.DataFrame({"Hours": [subset[minutes_column].sum() / 60]})

    def _production_hours(column: str) -> pd.DataFrame:
        if group_columns:
            return production_df.groupby(group_columns)[column].sum().rename("Hours").reset_index()
        return pd.DataFrame({"Hours": [production_df[column].sum()]})

    is_minor_stop = ((downtime_df["PlannedStoppage"] == "No") & ~downtime_df["UnplannedFailure"]
                      & ~downtime_df["IsChangeoverSetup"])
    breakdown = _hours(downtime_df, downtime_df["UnplannedFailure"], "DowntimeDurationMin")
    breakdown["LossCategory"] = "Quebras (falha não planejada)"
    changeover = _hours(downtime_df, downtime_df["IsChangeoverSetup"], "DowntimeDurationMin")
    changeover["LossCategory"] = "Setup / troca"
    minor_stop = _hours(downtime_df, is_minor_stop, "DowntimeDurationMin")
    minor_stop["LossCategory"] = "Paradas breves / idling"

    production_df = production_df.assign(
        _SpeedLossHours=production_df["RunTimeHours"] * (1 - production_df["Performance"]).clip(lower=0),
        _QualityLossHours=(production_df["RunTimeHours"] * production_df["Performance"].clip(lower=0)
                            * (1 - production_df["Quality"]).clip(lower=0)),
    )
    speed_loss = _production_hours("_SpeedLossHours")
    speed_loss["LossCategory"] = "Perda de velocidade"
    quality_loss = _production_hours("_QualityLossHours")
    quality_loss["LossCategory"] = "Perda de qualidade (sucata)"

    result = pd.concat([breakdown, changeover, minor_stop, speed_loss, quality_loss], ignore_index=True)
    return result[group_columns + ["LossCategory", "Hours"]]


# ---------------------------------------------------------------------------
# 5. SPC / AQL (statistical process control, quality sampling)
# ---------------------------------------------------------------------------

SPC_CONSTANTS = {
    2: dict(A2=1.880, D3=0.0, D4=3.267), 3: dict(A2=1.023, D3=0.0, D4=2.574),
    4: dict(A2=0.729, D3=0.0, D4=2.282), 5: dict(A2=0.577, D3=0.0, D4=2.114),
    6: dict(A2=0.483, D3=0.0, D4=2.004), 7: dict(A2=0.419, D3=0.076, D4=1.924),
    8: dict(A2=0.373, D3=0.136, D4=1.864), 9: dict(A2=0.337, D3=0.184, D4=1.816),
    10: dict(A2=0.308, D3=0.223, D4=1.777),
}
D2_CONSTANT = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}


def compute_control_limits(df: pd.DataFrame, group_columns: list[str], subgroup_size: int) -> pd.DataFrame:
    """X-bar/R control limits per group (characteristic x machine x mold x
    product), broadcast onto every row in that group so a chart can be
    built straight from the table."""
    constants = SPC_CONSTANTS[subgroup_size]
    df = df.copy()
    group = df.groupby(group_columns)
    df["XBarCL"] = group["XBar"].transform("mean")
    df["RangeRCL"] = group["RangeR"].transform("mean")
    df["XBarUCL"] = df["XBarCL"] + constants["A2"] * df["RangeRCL"]
    df["XBarLCL"] = df["XBarCL"] - constants["A2"] * df["RangeRCL"]
    df["RangeRUCL"] = constants["D4"] * df["RangeRCL"]
    df["RangeRLCL"] = constants["D3"] * df["RangeRCL"]
    df["OutOfControlXBar"] = (df["XBar"] > df["XBarUCL"]) | (df["XBar"] < df["XBarLCL"])
    df["OutOfControlRange"] = (df["RangeR"] > df["RangeRUCL"]) | (df["RangeR"] < df["RangeRLCL"])
    return df


def compute_process_capability(df: pd.DataFrame, group_columns: list[str], subgroup_size: int,
                                measurement_columns: list[str] | None = None) -> pd.DataFrame:
    """Cp/Cpk use WITHIN-subgroup variation (what the process can do on a
    good day); Pp/Ppk use TOTAL variation (closer to what the customer
    actually receives) -- the standard deviation of every individual
    measurement in the group (M1..Mn across all its subgroups), NOT the
    standard deviation of the subgroup averages (XBar). Those two are easy
    to conflate but are not the same statistic: XBar's spread is deflated
    by within-subgroup averaging (roughly by sqrt(subgroup_size)), so
    computing Pp/Ppk from it systematically overstates capability -- pass
    `measurement_columns` (e.g. ["M1",...,"M10"]) to compute it correctly
    from the individual observations. A large Cp-Cpk gap means the process
    isn't centered on target, not just too spread out."""
    d2 = D2_CONSTANT[subgroup_size]
    df = df.copy()
    group = df.groupby(group_columns)
    average_range = group["RangeR"].transform("mean")
    within_subgroup_std = average_range / d2
    grand_average = group["XBar"].transform("mean")

    df["Cp"] = (df["USL"] - df["LSL"]) / (6 * within_subgroup_std)
    df["Cpk"] = np.minimum((df["USL"] - grand_average) / (3 * within_subgroup_std),
                            (grand_average - df["LSL"]) / (3 * within_subgroup_std))

    if measurement_columns:
        individual = df[group_columns + measurement_columns].melt(
            id_vars=group_columns, value_vars=measurement_columns, value_name="Measurement"
        ).dropna(subset=["Measurement"])
        overall_std_by_group = individual.groupby(group_columns)["Measurement"].std()
        overall_std = pd.Series(df.set_index(group_columns).index.map(overall_std_by_group), index=df.index)
    else:
        overall_std = group["XBar"].transform("std")
    df["Pp"] = (df["USL"] - df["LSL"]) / (6 * overall_std)
    df["Ppk"] = np.minimum((df["USL"] - grand_average) / (3 * overall_std),
                            (grand_average - df["LSL"]) / (3 * overall_std))

    nominal_value = df["Nominal"] if "Nominal" in df.columns else (df["USL"] + df["LSL"]) / 2
    overall_std_with_target_shift = np.sqrt(overall_std ** 2 + (grand_average - nominal_value) ** 2)
    df["Cpm"] = (df["USL"] - df["LSL"]) / (6 * overall_std_with_target_shift)
    df["SigmaLevel"] = df["Cpk"] * 3 + 1.5
    return df


def compute_attribute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Defect rate (p-chart), DPU and DPMO -- one defect opportunity per
    unit, since each row is one characteristic on one lot."""
    df = df.copy()
    df["DefectRateP"] = df["DefectsFound"] / df["SampleSize"]
    df["DPU"] = df["DefectsFound"] / df["SampleSize"]
    df["DPMO"] = df["DPU"] * 1_000_000
    return df


# ---------------------------------------------------------------------------
# 6. MAINTENANCE
# ---------------------------------------------------------------------------

PLANNED_STOPPAGE_REASONS = {
    "Mold Change / Setup", "Color Change / Screen Setup", "Ribbon Change / Setup",
    "Scheduled Cleaning", "Screen Cleaning", "Planned Preventive Maintenance",
    "Meal Break (Shift 3 - No Relief Crew, 10Min Shutdown + 60Min Break + 10Min Startup)",
}


def add_maintenance_info(downtime: pd.DataFrame) -> pd.DataFrame:
    """Stoppage duration in minutes, plus flags for genuine unplanned
    failure, changeover/setup, and preventive maintenance."""
    df = downtime.copy()
    start = pd.to_timedelta(df["StoppageStartTime"].astype(str))
    end = pd.to_timedelta(df["StoppageEndTime"].astype(str))
    duration_minutes = (end - start).dt.total_seconds() / 60.0
    df["DowntimeDurationMin"] = duration_minutes.where(duration_minutes >= 0, duration_minutes + 24 * 60)
    df["UnplannedFailure"] = classify_stoppage(df)
    df["IsChangeoverSetup"] = df["StoppageReason"].str.contains("Change / Setup|Change/Setup", case=False, na=False, regex=True)
    df["IsPreventiveMaintenance"] = df["StoppageReason"].str.contains("Preventive Maintenance", case=False, na=False)
    return df


# ---------------------------------------------------------------------------
# 7. QUALITY ASSURANCE -- customer complaints, suppliers, NC/CAPA
# ---------------------------------------------------------------------------

def compute_days_between(df: pd.DataFrame, start_column: str, end_column: str, new_column_name: str) -> pd.DataFrame:
    """Generic days-between helper (complaint resolution, supplier response,
    CAPA closure). If the end date doesn't exist yet, the result is simply
    left NaN -- the record is still open, no special handling needed."""
    df = df.copy()
    df[new_column_name] = (pd.to_datetime(df[end_column]) - pd.to_datetime(df[start_column])).dt.days
    return df


def compute_complaints_per_million_shipped(complaints: pd.DataFrame, sales: pd.DataFrame,
                                            group_columns: list[str] | None = None) -> pd.Series:
    """Adjusts complaint count by quantity shipped, so a big customer
    doesn't automatically look "worse" than a small one just by buying more."""
    if group_columns:
        complaint_count = complaints.groupby(group_columns).size()
        shipped_quantity = sales.groupby(group_columns)["ShippedQty"].sum()
    else:
        complaint_count = pd.Series({"Total": len(complaints)})
        shipped_quantity = pd.Series({"Total": sales["ShippedQty"].sum()})
    return (complaint_count / shipped_quantity * 1_000_000).rename("ComplaintsPerMillionShipped")


def compute_supplier_approval_rate(lot_disposition: pd.DataFrame,
                                    group_columns: list[str] = ("SupplierId",)) -> pd.DataFrame:
    """Share of a supplier's incoming lots Accepted outright (excludes
    Accepted with Deviation and Rejected)."""
    counts = (lot_disposition.groupby(list(group_columns))["FinalDecision"]
              .value_counts(normalize=True).unstack(fill_value=0))
    counts["ApprovalRatePct"] = counts.get("Accepted", 0) * 100
    return counts
