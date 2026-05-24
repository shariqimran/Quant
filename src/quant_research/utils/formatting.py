"""Display formatting helpers."""


def format_currency(value):
    """Format a numeric value as USD currency."""
    return f"${value:,.2f}"


def format_percentage(value):
    """Format a numeric value as a percentage."""
    return f"{value:.2f}%"

