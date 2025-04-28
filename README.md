# Mutual Funds Scraping and Analysis

This project is designed to scrape mutual fund data from the [MFAPI](https://www.mfapi.in/) and provide analysis and visualization tools for mutual fund performance.

## Features

- Scrapes mutual fund data and stores it in CSV files.
- Provides a dashboard for analyzing and comparing mutual fund performance.
- Visualizes NAV growth, cumulative returns, moving averages, volatility, and drawdowns.

## Project Structure

- `app.py`: Streamlit app for data visualization and analysis.
- `scraper.py`: Script to scrape mutual fund data from the API.
- `test/`: Folder containing individual mutual fund data in CSV format.
- `all_mf.csv`: Master file containing all mutual fund schemes and their codes.
- `env/`: Virtual environment for the project.

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yaswanth33-ui/MutualScrape.git
   ```
2. Navigate to the project directory:
   ```bash
   cd MutualScrape
   ```
3. Create a virtual environment:
   ```bash
   python -m venv env
   ```
4. Activate the virtual environment:
   - On Windows:
     ```bash
     .\env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run the scraper to download data:
   ```bash
   python scraper.py
   ```
7. Launch the Streamlit app:
   ```bash
   streamlit run app.py
   ```
   
Open your web browser and go to http://localhost:8501 (or http://0.0.0.0:8501 if needed for accessibility) to interact with the application.


## Contribution Guidelines

We welcome contributions to improve this project. Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push your changes to your fork:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

Contact For any inquiries or support, please reach out at yaswanthreddypanem@gmail.com .
