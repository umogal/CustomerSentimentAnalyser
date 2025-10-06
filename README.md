![](https://github.com/umogal/CustomerSentimentAnalyser/blob/main/splash_logo_um.jpg)
### Customer Feedback Sentiment and Text Analysis Tool

Developed as a command-line utility in Python, this tool analyzes sentiment and extracts key features from textual data using the TextBlob library. Initially created locally in my spare time for experimentation and learning, the GitHub repository was established after ensuring the tool was designed for reliable operation in production environments.

# **W.I.P : Expect Breaking Changes and New Features** 

**Looking for contributors!**

>  **License & Usage:** This FOSS project is licensed under the **AGPL-3.0**. Free for personal and commercial use under the AGPL terms. Unauthorized reselling, relicensing, or white-labeling requires written permission. Contact me directly for licensing. Someone DMed me about a "repo thief" trying to pass this off as their own, frankly, I’m flattered. - @umogal




## Features

* **Sentiment Analysis:** Calculates polarity (positivity/negativity) and subjectivity scores.
* **Sentiment Classification:** Categorizes text as Positive, Negative, or Neutral based on configurable thresholds.
* **Input Flexibility:** Accepts text directly via command-line argument or reads from a specified file.
* **Sentence-Level Analysis:** Option to analyze sentiment for each sentence within the input.
* **Noun Phrase Extraction:** Identifies and lists key noun phrases in the text.
* **Language Detection:** Attempts to detect the language of the input text.
* **Text Statistics:** Provides basic metrics like word and sentence counts.
* **Error Handling:** Robust handling and logging of potential issues during file reading or analysis.
* **Logging:** Configurable logging levels for monitoring operational details.
* **Output Formats:** Presents results in human-readable plain text or structured JSON format.

## Requirements

* Python 3.6 or higher.
* The `TextBlob` library and its necessary corpora.

## Installation

1.  Ensure you have Python installed.
2.  Save the provided Python script (e.g., `sentiment.py`).
3.  Save the provided `requirements.txt` file in the same directory.
4.  Install the required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

5.  Download the necessary TextBlob corpora for full functionality, particularly for language detection:

    ```bash
    python -m textblob.download_corpora
    ```

## Usage

The tool is executed from the command line. It requires either the `-t` (text) or `-f` (file) argument to specify the input.

```bash
python sentiment.py [INPUT_OPTIONS] [ANALYSIS_OPTIONS] [OUTPUT_OPTIONS] [CONFIGURATION_OPTIONS]
````

### Input Options (Mutually Exclusive)

  * `-t TEXT`, `--text TEXT`: Provide the text string directly for analysis.
    ```bash
    python sentiment.py --text "This service is exceptionally efficient and utterly reliable."
    ```
  * `-f FILE`, `--file FILE`: Provide the path to a text file for analysis.
    ```bash
    python sentiment.py --file "path/to/your/feedback.txt"
    ```
    *Note: Processing very large files may require significant memory.*

### Analysis Options

  * `-s`, `--sentence-level`: Analyze and report sentiment for each sentence individually, in addition to the overall text.
    ```bash
    python sentiment.py --text "The first part was excellent. The second, less so." --sentence-level
    ```
  * `--noun-phrases`: Extract and display key noun phrases found in the input text.
    ```bash
    python sentiment.py --text "The quick brown fox jumps over the lazy dog." --noun-phrases
    ```
  * `--detect-lang`: Attempt to detect the language of the input text.
    ```bash
    python sentiment.py --text "¿Cómo está usted?" --detect-lang
    ```

### Output Options

  * `-j`, `--json`: Output the analysis results in a structured JSON format. This is recommended for integration with other systems or scripting.
    ```bash
    python sentiment.py --file "report.txt" --json
    ```

### Configuration Options

  * `--pos-threshold FLOAT`: Set the polarity threshold for classifying text as 'Positive' (default: 0.1). Polarity scores equal to or above this value are classified as Positive.
  * `--neg-threshold FLOAT`: Set the polarity threshold for classifying text as 'Negative' (default: -0.1). Polarity scores equal to or below this value are classified as Negative. Scores between the positive and negative thresholds are classified as Neutral.
    ```bash
    python sentiment.py --text "It was okay." --pos-threshold 0.2 --neg-threshold -0.2
    ```
  * `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Set the verbosity level for logging messages (default: WARNING). Logs are written to standard error (stderr).
    ```bash
    python sentiment.py --text "Test log level" --log-level INFO
    ```

## Output

The output format depends on the presence of the `-j` or `--json` flag.

  * **Plain Text Output (Default):** Provides a human-readable summary including overall sentiment, text statistics, detected language (if requested), noun phrases (if requested), and sentence-level analysis (if requested).
  * **JSON Output (`-j`):** Outputs a JSON object containing all analysis results, suitable for programmatic consumption.

In case of errors (e.g., file not found, analysis failure), an error message will be printed to standard error, and the script will exit with a non-zero status code. Detailed error information is also available via logging, depending on the configured `--log-level`.

## Notes

  * Sentiment analysis, while useful, is an approximation. TextBlob's analysis is based on its training data and algorithms and may not perfectly capture the nuances of all human language.
  * Performance is generally good for typical text inputs. For extremely large files, memory consumption could become a factor.

<!-- end list -->

