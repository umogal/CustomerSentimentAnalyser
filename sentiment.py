# SPDX-License-Identifier: AGPL-3.0-or-later
# ©2025 umogal
import argparse
import sys
import json
import logging
import time # For potential performance tracking, though TextBlob's speed is inherent

from textblob import TextBlob
from textblob.exceptions import TextBlobException, TranslatorError, NotTranslated

# --- Logging Setup ---
# Configure a basic logger. Default level is WARNING.
# Allows setting level via --log-level flag.
logging.basicConfig(level=logging.WARNING, stream=sys.stderr,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# Acquire the logger for this module.
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Analyzes text or files, supports sentence-level analysis, language detection,
    noun phrase extraction, and classification based on thresholds.
    Integrates logging for operational visibility.
    """

    def __init__(self, positive_threshold=0.1, negative_threshold=-0.1):
        """
        Initializes the analyzer with classification thresholds.

        Args:
            positive_threshold (float): Polarity value >= this is classified as positive.
            negative_threshold (float): Polarity value <= this is classified as negative.
                                        Values between thresholds are neutral.
        """
        # Validate thresholds and log a warning if they are illogical.
        if not (-1.0 <= negative_threshold <= positive_threshold <= 1.0):
            logger.warning("Classification thresholds are set illogically (%f, %f). Using defaults (-0.1, 0.1).",
                           negative_threshold, positive_threshold)
            self.positive_threshold = 0.1
            self.negative_threshold = -0.1
        else:
            self.positive_threshold = positive_threshold
            self.negative_threshold = negative_threshold
            logger.debug("Initialized Analyzer with thresholds: Pos=%.2f, Neg=%.2f",
                         self.positive_threshold, self.negative_threshold)

    def classify_sentiment(self, polarity):
        """
        Classifies sentiment based on polarity and defined thresholds.

        Args:
            polarity (float): The polarity score.

        Returns:
            str: 'Positive', 'Negative', or 'Neutral'.
        """
        if polarity >= self.positive_threshold:
            return "Positive"
        elif polarity <= self.negative_threshold:
            return "Negative"
        else:
            return "Neutral"

    def analyze_text(self, text, sentence_level=False, include_noun_phrases=False, detect_language=False):
        """
        Analyzes the sentiment and features of a given text string.

        Args:
            text (str): The input text.
            sentence_level (bool): If True, analyze each sentence separately.
            include_noun_phrases (bool): If True, extract noun phrases.
            detect_language (bool): If True, attempt language detection.

        Returns:
            dict: Analysis results. Includes 'error' key if analysis fails.
                  Structure depends on flags like sentence_level and json output.
        """
        if not text or not isinstance(text, str) or not text.strip():
            # Log and return error for empty input.
            logger.warning("Attempted to analyze empty or whitespace-only text.")
            return {"error": "The text provided is devoid of content, My Lord. Analysis requires substance."}

        logger.info("Starting analysis for text snippet (first 50 chars): '%s...'", text[:50])
        start_time = time.time()

        try:
            blob = TextBlob(text)
            results = {"analysis_timestamp": time.time()} # Timestamp for record-keeping

            # --- Core Sentiment Analysis ---
            if sentence_level:
                results['sentences'] = []
                logger.debug("Analyzing sentiment at sentence level.")
                for i, sentence in enumerate(blob.sentences):
                    try:
                        sentiment = sentence.sentiment
                        sentence_data = {
                            "text": str(sentence),
                            "polarity": sentiment.polarity,
                            "subjectivity": sentiment.subjectivity,
                            "classification": self.classify_sentiment(sentiment.polarity)
                        }
                        results['sentences'].append(sentence_data)
                        logger.debug("Analyzed sentence %d: Polarity=%.4f", i+1, sentiment.polarity)
                    except Exception as e:
                         # Log but attempt to continue if a single sentence fails.
                         logger.error("Error analyzing sentence %d: %s", i, e, exc_info=True)
                         results['sentences'].append({"text": str(sentence), "error": str(e)})

                # Still provide overall summary
                overall_sentiment = blob.sentiment
                results['overall'] = {
                    "polarity": overall_sentiment.polarity,
                    "subjectivity": overall_sentiment.subjectivity,
                    "classification": self.classify_sentiment(overall_sentiment.polarity)
                }
                logger.debug("Overall sentiment calculated: Polarity=%.4f", overall_sentiment.polarity)
            else:
                # Analyze the entire text block.
                overall_sentiment = blob.sentiment
                results['overall'] = {
                    "polarity": overall_sentiment.polarity,
                    "subjectivity": overall_sentiment.subjectivity,
                    "classification": self.classify_sentiment(overall_sentiment.polarity)
                }
                logger.debug("Overall sentiment calculated: Polarity=%.4f", overall_sentiment.polarity)

            # --- Additional Analysis Features ---
            results['text_stats'] = {
                "word_count": len(blob.words),
                "sentence_count": len(blob.sentences)
            }
            logger.debug("Calculated text statistics: Words=%d, Sentences=%d",
                         results['text_stats']['word_count'], results['text_stats']['sentence_count'])


            if include_noun_phrases:
                # Extracting key noun phrases.
                noun_phrases = [str(phrase) for phrase in blob.noun_phrases]
                results['noun_phrases'] = noun_phrases
                logger.debug("Extracted %d noun phrases.", len(noun_phrases))

            if detect_language:
                # Attempting language identification.
                try:
                    lang = blob.detect_language()
                    results['detected_language'] = lang
                    logger.debug("Detected language: %s", lang)
                except (TranslatorError, NotTranslated) as e:
                    # TextBlob's language detection relies on translation services internally.
                    logger.warning("Could not reliably detect language: %s. Input text might be too short or unusual.", e)
                    results['detected_language_error'] = str(e)
                except Exception as e:
                     # Catching any other language detection issues.
                     logger.error("Unexpected error during language detection: %s", e, exc_info=True)
                     results['detected_language_error'] = str(e)


            end_time = time.time()
            results['processing_time_seconds'] = end_time - start_time
            logger.info("Analysis completed in %.4f seconds.", results['processing_time_seconds'])

            return results

        except TextBlobException as e:
            # Log specific TextBlob errors with trace back.
            logger.error("A TextBlob-specific issue occurred during analysis: %s", e, exc_info=True)
            return {"error": f"A TextBlob-specific issue occurred: {e}. The library appears... temperamental."}
        except Exception as e:
            # Log any other unexpected exceptions with trace back.
            logger.critical("A critical unexpected error arose during analysis: %s", e, exc_info=True)
            return {"error": f"A critical unexpected error arose during analysis: {e}. Immediate attention required."}

    def analyze_file(self, file_path, sentence_level=False, include_noun_phrases=False, detect_language=False):
        """
        Reads text from a file and performs sentiment and feature analysis.

        Args:
            file_path (str): The path to the input file.
            sentence_level (bool): If True, analyze each sentence separately.
            include_noun_phrases (bool): If True, extract noun phrases.
            detect_language (bool): If True, attempt language detection.

        Returns:
            dict: Analysis results. Includes 'error' key if file reading or analysis fails.
        """
        logger.info("Attempting to read file: %s", file_path)
        try:
            # Attempting to read the entire file content.
            # Note: For extremely large files, reading all at once can consume significant memory.
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info("Successfully read file: %s. File size: %d characters.", file_path, len(text))
            # Proceed with the analysis of the file's content.
            return self.analyze_text(text,
                                     sentence_level=sentence_level,
                                     include_noun_phrases=include_noun_phrases,
                                     detect_language=detect_language)
        except FileNotFoundError:
            # Log file not found errors.
            logger.error("File not found at path: %s.", file_path)
            return {"error": f"File not found at path: {file_path}. Ensure its location is correct."}
        except IOError as e:
            # Log general IO errors during file reading.
            logger.error("Error reading file %s: %s", file_path, e, exc_info=True)
            return {"error": f"Error reading file {file_path}: {e}. The file seems... resistant."}
        except MemoryError:
             # Log memory errors specifically for very large files.
             logger.critical("Memory Error: File %s is too large to read into memory.", file_path)
             return {"error": f"Memory Error: File {file_path} is too large to process with current resources."}
        except Exception as e:
            # Log any other unforeseen file-related issues.
            logger.critical("An unexpected error occurred while processing file %s: %s", file_path, e, exc_info=True)
            return {"error": f"An unexpected error occurred while processing file {file_path}: {e}. Consult the logs."}


def main():
    """
    Main function to parse arguments, configure logging, and execute analysis.
    """
    parser = argparse.ArgumentParser(
        description="An enhanced command-line tool for sentiment and text analysis using TextBlob.",
        formatter_class=argparse.RawTextHelpFormatter,
        # Updated epilog reflecting enhanced capabilities and status.
        epilog="Analyzes textual inputs for emotional, factual, and structural elements.\n"
               "Equipped with logging and error handling for more reliable operation.\n"
               "Proceed with analysis."
    )

    # --- Input Options (Mutually Exclusive) ---
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-t", "--text",
        help="Direct text string for analysis."
    )
    input_group.add_argument(
        "-f", "--file",
        help="Path to a text file for analysis.\n"
             "Note: Very large files may cause Memory Errors."
    )

    # --- Analysis Options ---
    parser.add_argument(
        "-s", "--sentence-level",
        action="store_true",
        help="Analyze sentiment for each sentence individually."
    )
    parser.add_argument(
        "--noun-phrases",
        action="store_true",
        help="Extract and include key noun phrases found in the text."
    )
    parser.add_argument(
        "--detect-lang",
        action="store_true",
        help="Attempt to detect the language of the input text."
    )

    # --- Output Options ---
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output results in JSON format (recommended for scripting/automation)."
    )

    # --- Configuration Options ---
    parser.add_argument(
        "--pos-threshold",
        type=float,
        default=0.1,
        help="Polarity threshold for 'Positive' classification (default: 0.1).\n"
             "Values >= threshold are Positive."
    )
    parser.add_argument(
        "--neg-threshold",
        type=float,
        default=-0.1,
        help="Polarity threshold for 'Negative' classification (default: -0.1).\n"
             "Values <= threshold are Negative. Values between are Neutral."
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging verbosity level (default: WARNING).\n"
             "DEBUG: Detailed logs\nINFO: General progress\nWARNING: Potential issues\nERROR: Analysis failed\nCRITICAL: System-level problems"
    )

    args = parser.parse_args()

    # --- Configure Logging Level ---
    # Set the root logger level based on the command-line argument.
    logging.getLogger().setLevel(args.log_level.upper())
    logger.info("Logging level set to %s", args.log_level.upper())
    logger.debug("Command line arguments parsed: %s", args)

    # --- Initialize and Run Analysis ---
    analyzer = SentimentAnalyzer(
        positive_threshold=args.pos_threshold,
        negative_threshold=args.neg_threshold
    )

    # Determine input source and perform analysis.
    results = None # Initialize results outside the if block

    if args.text:
        logger.info("Initiating analysis for direct text input.")
        results = analyzer.analyze_text(
            args.text,
            sentence_level=args.sentence_level,
            include_noun_phrases=args.noun_phrases,
            detect_language=args.detect_lang
        )
    elif args.file:
        logger.info("Initiating analysis for file input: %s", args.file)
        results = analyzer.analyze_file(
            args.file,
            sentence_level=args.sentence_level,
            include_noun_phrases=args.noun_phrases,
            detect_language=args.detect_lang
        )

    # --- Present Results ---
    if results is None:
         # Should not happen with required=True, but as a safeguard.
         logger.critical("Analysis did not produce results. Logic error?")
         sys.exit(1)


    if "error" in results:
        # An error occurred during analysis or file reading.
        # Error is already logged by the respective analysis method.
        print(f"Operation failed: {results['error']}", file=sys.stderr)
        sys.exit(1) # Exit with a non-zero status to indicate failure.

    if args.json:
        # Output in JSON format for easy parsing by other systems.
        logger.info("Outputting results in JSON format.")
        try:
            print(json.dumps(results, indent=4, ensure_ascii=False)) # ensure_ascii=False for better human readability of non-ASCII chars in output
        except TypeError as e:
            logger.critical("Failed to serialize results to JSON: %s. Results structure issue?", e, exc_info=True)
            print(f"Output Error: Could not format results as JSON - {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Output in human-readable plain text format.
        logger.info("Outputting results in plain text format.")
        print("\n--- Sentiment and Text Analysis Results ---")

        # Display core sentiment and stats
        if 'overall' in results:
            overall = results['overall']
            print("Overall Analysis:")
            print(f"  Polarity:         {overall['polarity']:.4f}")
            print(f"  Subjectivity:     {overall['subjectivity']:.4f}")
            print(f"  Classification:   {overall['classification']}")

        if 'text_stats' in results:
             stats = results['text_stats']
             print("Text Statistics:")
             print(f"  Word Count:       {stats['word_count']}")
             print(f"  Sentence Count:   {stats['sentence_count']}")

        if 'detected_language' in results:
            print(f"Detected Language:  {results['detected_language']}")
        elif 'detected_language_error' in results:
             print(f"Language Detection: Failed - {results['detected_language_error']}")


        if 'noun_phrases' in results and results['noun_phrases']:
            # List extracted noun phrases if found.
            print("\nKey Noun Phrases:")
            # Limit display of noun phrases for brevity in plain text
            display_phrases = results['noun_phrases'][:10] # Show first 10
            print(f"  {', '.join(display_phrases)}{'...' if len(results['noun_phrases']) > 10 else ''}")


        if 'sentences' in results:
            # If sentence-level analysis was requested, list results for each.
            print("\nSentence-Level Analysis:")
            for i, sentence_result in enumerate(results['sentences']):
                 if 'error' in sentence_result:
                     print(f"  Sentence {i+1}: Analysis Failed - {sentence_result['error']}")
                     continue # Skip to next sentence if analysis failed for this one

                 # Ellipsize long sentences for readability in the output.
                 display_text = sentence_result['text'] if len(sentence_result['text']) < 80 else sentence_result['text'][:77] + "..."
                 print(f"  Sentence {i+1}: \"{display_text}\"")
                 print(f"    Polarity:       {sentence_result['polarity']:.4f}")
                 print(f"    Subjectivity:   {sentence_result['subjectivity']:.4f}")
                 print(f"    Classification: {sentence_result['classification']}")

        # Display processing time
        if 'processing_time_seconds' in results:
             print(f"\nProcessing Time:  {results['processing_time_seconds']:.4f} seconds")


        print("---------------------------------------------")
        # A concluding note on the nature of the scores.
        print("\nNote:")
        print("  Polarity: -1.0 (Negative) to +1.0 (Positive). 0.0 is Neutral.")
        print("  Subjectivity: 0.0 (Objective) to +1.0 (Subjective).")
        print(f"  Classification based on thresholds: >={args.pos_threshold} (Positive), <={args.neg_threshold} (Negative), else Neutral.")


if __name__ == "__main__":
    # Ensure the script runs when executed directly.
    main()
