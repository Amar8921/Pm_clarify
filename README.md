# PM-Clarify

PM-Clarify is an application built with Django that utilizes AI models from Azure Document Analyzer to convert files into JSON formatted data.

## Installation

1. Install the required dependencies:

    ```shell
    pip install -r requirements.txt
    ```

2. Start the required services using Docker Compose:

    ```shell
    docker-compose up -d
    ```

## Usage

1. Initialize the database and populate data by running the following command:

    ```shell
    python manage.py populate_data
    ```

    This command will populate the database with the necessary data.

2. Start the application:

    ```shell
    python manage.py runserver
    ```

    The application will be accessible at `http://localhost:8000`.

## Common issues

### zsh: command not found: pip

This issue usually occurs when Python or pip is not installed correctly, or the path to Python and pip is not set correctly in your system's PATH variable.

Here are some steps you can take to resolve this issue:

1. Check if Python is installed correctly by running `python --version` or `python3 --version` in your terminal.

2. Check if pip is installed by running `pip --version` or `pip3 --version` in your terminal.

3. If Python is installed but pip is not, you can install pip by running `python -m ensurepip --upgrade` or `python3 -m ensurepip --upgrade` in your terminal.

4. If Python and pip are installed but the `pip` command is not recognized, it's likely that the path to Python and pip is not set correctly in your system's PATH variable. You can add the path to Python and pip to your system's PATH variable by following the instructions specific to your operating system.

### ModuleNotFoundError: No module named 'django'

This error usually occurs when the Django module is not installed in your Python environment.

Here are some steps you can take to resolve this issue:

1. Check if Django is installed by running `python -m django --version` in your terminal. If Django is installed correctly, this command should return the version of Django that's installed on your system.

2. If Django is not installed, you can install it by running `pip install django` in your terminal.

3. If you're working in a project that has a `requirements.txt` file, make sure to install all the required modules by running `pip install -r requirements.txt` in your terminal.

Remember to activate your virtual environment before installing the modules if you're using one.

## License

This project is licensed under the [MIT License](LICENSE).
