import os

def get_theme_path(theme_name: str) -> str:

    base_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "../../external/ctk_theme_builder/user_themes"
        )
    )

    filename=f"{theme_name}.json"

    return os.path.join(base_path, filename)