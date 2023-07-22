
# UIUC Course Explorer Scraper

A python webscraper to scrape courses from https://courses.illinois.edu/

# Dependencies
Python 3
Beautiful Soup 4
pandas
tqdm
requests
argparse

You can install these dependencies with pip:

`pip install -r requirements.txt`

# Usage

To run the script, use the following command:

`python scraper.py <term> <year> --rate_limit <rate_limit>`

* `<term>`: The academic term. It can be 'fall', 'spring', 'winter', or 'summer'.
* `<year>`: The year of the academic term. It must be a four-digit number between 1900 and two years into the future from the current year.
* `<rate_limit>`: (Optional) The time (in seconds) the script will wait between each request to the server. It is set to 0.1 seconds by default.

# Output

The script will produce a CSV file named `<term>-<year>-courses.csv`. The CSV file will contain the following columns:

* Subject: The name of the subject (e.g., Computer Science)
* Subject Abbreviation: The abbreviation of the subject (e.g., CS)
* Course: The course number (e.g., 101)
* Name: The name of the course (e.g., Introduction to Computer Science)
* Description: A brief description of the course
* Credit Hours: The number of credit hours for the course
* Degree Attributes: Any general education categories the course falls under

# Notes

The script is not yet fully optimized. Currently, it writes all data to disk at once at the end of the scraping process. In the future, it is planned to add functionality to write data in chunks while iterating, which would help manage memory usage more effectively.

Another area for improvement is to add exponential backoff for handling request errors and rate limiting.

If the provided URL does not exist or an exception occurs during the scraping process, the script will print an error message to the console.

# Disclaimer

Please use this script responsibly, and respect the server's terms of service and potential rate limits. Overloading a server with too many requests in a short period can cause issues for the server and potentially get your IP address blocked. The `--rate_limit` argument can be used to space out the requests to the server.
