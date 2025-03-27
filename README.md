# Web Scraping with Playwright

This repository contains tools and examples for web scraping using Playwright, a powerful browser automation library.

## Overview

This project demonstrates how to use Playwright to scrape content from various websites, including:

- Basic website title extraction
- Quotes from literary websites
- YouTube video descriptions and comments

## Features

- Browser automation with headless or visible mode
- Handling of cookie consent dialogs
- Robust selectors for different website structures
- YouTube-specific functionality:
  - Search handling
  - Video interaction
  - Comment extraction
  - Description capture

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/playwright-web-scraping.git
   cd playwright-web-scraping
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Install the required browser drivers:
   ```bash
   python -m playwright install chromium
   ```

## Usage

### Basic Website Scraping

To extract the title of a website:

```bash
python first_scraper.py
```

### Scraping Quotes

To scrape quotes from quotes.toscrape.com:

```bash
python scrape_quotes.py
```

### YouTube Scraper

To scrape information from YouTube videos:

```bash
python youtube_scraper.py
```

The YouTube scraper will:

1. Navigate to YouTube
2. Handle any consent dialogs
3. Search for the term defined in the script
4. Click on the first video result
5. Extract the video description
6. Capture comments
7. Save the results to `youtube_results.txt`

## Advanced Configuration

You can modify the following parameters in the scripts:

- In `youtube_scraper.py`:
  - `URL`: The base YouTube URL
  - `SEARCH_TERM`: The term to search for on YouTube
  - Headless mode: Set `headless=True` to run without a visible browser

## Documentation

The repository includes a comprehensive guide on web scraping with Playwright in the `guide.md` file, which covers:

- Web scraping concepts
- Playwright features
- AgentQL integration
- Script structure explanation
- Detailed code walkthrough

## Dependencies

Main dependencies include:

- playwright - For browser automation
- agentql - For simplified element selection
- python-dotenv - For environment variable management
- tf-playwright-stealth - For bot detection avoidance

See `requirements.txt` for a complete list.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

Web scraping may be subject to legal restrictions and website terms of service. Always:

- Review the website's robots.txt file
- Check the terms of service before scraping
- Implement rate limiting to avoid overloading servers
- Be respectful of the website's resources

This code is provided for educational purposes only.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Cécile Hirschauer
