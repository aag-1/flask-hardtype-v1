from flask import Flask, render_template, request
import time
from random_word import RandomWords

app = Flask(__name__)

# Function to calculate adjusted score, error, and WPM
def calculate_wpm_and_score(input_text, generated_words, typing_duration):
    score = 0
    error = 0

    # Process the input text and compare it with generated words
    input_words = input_text.split()
    outputchecktext = "".join(generated_words)
    usertypechecktext = "".join(input_text.split())

    numbernotwritten = len(generated_words) - len(input_words)

    txtoutputreformed = outputchecktext[:len(usertypechecktext)]

    for i in range(len(txtoutputreformed)):
        if txtoutputreformed[i] == usertypechecktext[i]:
            score += 1
        else:
            error += 1

    # Word-by-word comparison
    score1 = 0
    error1 = 0

    for i in range(len(generated_words)):  # loop over generated words
        if i < len(input_words):  # only process if user input word exists
            word1 = generated_words[i]
            word2 = input_words[i]

            # Compare the characters of the words
            min_len = min(len(word1), len(word2))
            for k in range(min_len):
                if word1[k] == word2[k]:
                    score1 += 1
                else:
                    error1 += 1

            # Count the remaining characters as errors if words are of different lengths
            if len(word1) != len(word2):
                error1 += abs(len(word1) - len(word2))

    # Calculate final scores
    adjusted_score = (score1 + score) / 2
    adjusted_error = (error1 + error + numbernotwritten) / 3

    # WPM Calculation based on the adjusted score and errors
    numerator = (adjusted_score - adjusted_error)
    denominator = (typing_duration * numbernotwritten) / 60
    wpm = numerator / denominator if denominator > 0 else 0

    return round(wpm), adjusted_score, adjusted_error


@app.route("/", methods=["GET", "POST"])
def index():
    r = RandomWords()

    # Generate random words (GET request)
    words = [r.get_random_word() for _ in range(15)]

    # Handle form submission (POST request)
    wpm = None
    adjusted_score = None
    adjusted_error = None
    if request.method == "POST":
        input_text = request.form.get("input_text")
        start_time = request.form.get("start_time")

        # Ensure start_time is provided and not empty before converting to float
        if start_time:
            try:
                start_time = float(start_time)
                end_time = time.time()

                # Use the words sent in the form (hidden input field)
                words = request.form.get("words").split()

                # Calculate typing duration
                typing_duration = end_time - start_time

                # Calculate WPM, score, and error
                wpm, adjusted_score, adjusted_error = calculate_wpm_and_score(input_text, words, typing_duration)

                # After form submission, generate new words for the next session
                words = [r.get_random_word() for _ in range(15)]
            except ValueError:
                print("Error: start_time could not be converted to float")
        else:
            print("Error: start_time is missing or empty")

    return render_template("index.html", words=" ".join(words), wpm=wpm, adjusted_score=adjusted_score, adjusted_error=adjusted_error)


if __name__ == "__main__":
    app.run(debug=True)
