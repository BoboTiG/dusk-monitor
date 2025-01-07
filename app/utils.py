"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

def compute_rewards(blocks: set[int]) -> float:
    """
    Block generators get 80% + voting fractions (not computed here).
    Source: https://github.com/dusk-network/audits/blob/main/core-audits/2024-09_economic-protocol-design_pol-finance.pdf
    Source: https://github.com/dusk-network/rusk/blob/rusk-1.0.0/rusk/src/lib/node.rs#L132-L157
    """
    amount = 0.0
    for block in blocks:
        if block == 113_529_597:  # Last mint
            dusk = 0.05428
        elif block >= 100_915_201:  # Period 9
            dusk = 0.07757
        elif block >= 88_300_801:  # Period 8
            dusk = 0.15514
        elif block >= 75_686_401:  # Period 7
            dusk = 0.31027
        elif block >= 63_072_001:  # Period 6
            dusk = 0.62054
        elif block >= 50_457_601:  # Period 5
            dusk = 1.24109
        elif block >= 37_843_201:  # Period 4
            dusk = 2.48218
        elif block >= 25_228_801:  # Period 3
            dusk = 4.96435
        elif block >= 12_614_401:  # Period 2
            dusk = 9.9287
        elif block >= 1:  # Period 1
            dusk = 19.8574
        else:  # Genesis
            dusk = 0.0
        amount += dusk * 0.8
    return amount


def format_num(value: int) -> str:
    for unit in ("", "k"):
        if value < 1000:
            return f"{value:.03f}{unit}"
        value /= 1000
    return f"{value:,.03f}M"
