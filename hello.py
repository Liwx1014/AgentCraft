"""A simple hello world module with greeting functionality."""


def greet(name: str) -> str:
    """Generate a greeting message for a given name.

    Args:
        name: The name of the person to greet.

    Returns:
        A formatted greeting string.
    """
    return f"Hello, {name}!"


def main() -> None:
    """Main function to run when module is executed directly."""
    print(greet("World"))


if __name__ == "__main__":
    main()
