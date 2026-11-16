#import statements
from bakery import assert_equal
from dataclasses import dataclass
from drafter import *

set_website_title("Shirt Size Finder")
set_site_information(
    author="Andy Arrighi",
    description="Find the best-fitting shirt size across clothing brands.",
    sources=["UD CISC 106 Final Project"],
    planning=["ANDY (1).docx", "Copy of CS1 Final Project 1_ Design (1).pdf"],
    links=["https://github.com/"])

hide_debug_information()
set_website_framed(False)

BRANDS = ["Nike", "Adidas", "Underarmor", "Gap", "Carhartt"]
FITS = ["Slim", "Loose", "Regular"]
SIZES = ["XS", "S", "M", "L", "XL", "XXL"]

@dataclass
class ShirtRecommendation:
    """Represents a single saved shirt size recommendation."""
    brand: str
    size: str
    fit: str
    description: str
    
@dataclass
class State:
    """Tracks the user measurements, preference, and website history."""
    height: float
    weight: float
    preferred_fit: str
    brand: str
    saved_recommendations: list[ShirtRecommendation]

def is_valid_number(text:str)-> bool:
    """Returns True if the text represents a valid positive float."""
    cleaned = text.strip()
    if cleaned == "" or cleaned ==".":
        return False
    parts = cleaned.split(".")
    if len(parts) > 2:
        return False
    return "".join(parts).isdigit()
def calculate_base_size_index(height: float, weight: float, brand: str)-> int:
    """returns a strating index (0-5) in sizes based on stats and what brand"""
    score = (weight / 2.2) + (height - 60.0) * 1.5
    if brand == "Underarmor" or brand == "Nike":
        score += 4.0
    elif brand == "Carhartt":
        score += 5.0
    
    if score < 70:
        return 0
    elif score < 82:
        return 1
    elif score < 95:
        return 2
    elif score < 110:
        return 3
    elif score < 125:
        return 4
    return 5

def build_recommendation(state: State)-> ShirtRecommendation:
    """creates a shirt recommendation using user current state value"""
    size_index = calculate_base_size_index(
        state.height, state.weight, state.brand)
    if state.preferred_fit == "Slim" and size_index > 0:
        size_index -= 1
    elif state.preferred_fit == "Loose" and size_index < len(SIZES) - 1:
        size_index += 1
        
    chosen_size = SIZES[size_index]
    reason = (f'Based on {state.height} in, {state.weight} lbs, a '
        f"{state.preferred_fit} fit, and {state.brand}'s sizing chart.")
    return ShirtRecommendation(
        state.brand,
        chosen_size,
        state.preferred_fit,
        reason)

@route
def index(state: State)-> Page:
    """ displays the home page and description of shirt finder on website"""
    return Page(
        state,
        [
            Header("Shirt Size Finder"),
            "Find the right shirt size across brands based on your body "
            "measurements and fit preference.",
            Button("Get Started", measurements),
            Button("View Saved History", history)])

@route
def measurements(state: State, error_message: str = "") -> Page:
    """displays inputs for the user height and weight"""

    height_default = ""
    if state.height > 0:
        height_default = str(state.height)

    weight_default = ""
    if state.weight > 0:
        weight_default = str(state.weight)

    content = [
        Header("Step 1: Your Measurements"),
        "Enter your height (in inches) and weight (in pounds):"
    ]

    if error_message != "":
        content.append(error_message)

    content.append("Height (inches):")
    content.append(TextBox("height_text", height_default))
    content.append("Weight (lbs):")
    content.append(TextBox("weight_text", weight_default))
    content.append(Button("Next: Fit & Brand", preferences))
    content.append(Button("Back to Home", index))

    return Page(state, content)

@route
def preferences(state: State, height_text: str = "", weight_text: str = "")-> Page:
    """confirms and validates measurements and displays the fit/brand selector"""
    if height_text != "" or weight_text != "":
        if not is_valid_number(height_text) or not is_valid_number(weight_text):
            return measurements(
                state,
                "Please enter valid positive numbers for height and weight.")

        height_val = float(height_text)
        weight_val = float(weight_text)

        if height_val <= 0 or weight_val <= 0:
            return measurements(
                state,
                "Height and weight must both be greater than zero.")

        state.height = height_val
        state.weight = weight_val

    return Page(state,
        [Header("Step 2: Fit & Brand Preferences"),
            f"Current Measurements: {state.height} in, {state.weight} lbs",
            "Preferred Fit:",
            SelectBox("fit", FITS, state.preferred_fit),
            "Clothing Brand:",
            SelectBox("brand", BRANDS, state.brand),
            Button("Find My Size", recommendation),
            Button("Back to Measurements", measurements),])
@route
def recommendation(state: State, fit: str = "", brand: str = "")-> Page:
    """updates what user preffers and displays recommended size"""
    if fit != "":
        state.preferred_fit = fit
    if brand != "":
        state.brand = brand

    rec = build_recommendation(state)
    return Page(state,
        [Header("Your Recommended Shirt Size"),
            f"Brand: {rec.brand}",
            f"Recommended Size: {rec.size}",
            f"Preferred Fit: {rec.fit}",
            rec.description,
            Button("Save This Recommendation", save_recommendation),
            Button("View Saved History", history),
            Button("Start Over", index),])

@route
def save_recommendation(state: State)-> Page:
    """saves the currect recommendation to State and redirects to history"""
    rec = build_recommendation(state)
    state.saved_recommendations.append(rec)
    return history(state)

@route
def history(state: State)-> Page:
    """Display all saved shirt recommendations using a loop."""
    content: list = [Header("Saved Shirt Recommendations")]
    if len(state.saved_recommendations) == 0:
        content.append("You have no saved recommendations yet.")
    else:
        for item in state.saved_recommendations:
            content.append(f"{item.brand} - Size {item.size} ({item.fit} fit): "
                f"{item.description}")
        content.append(Button("Clear Saved History", clear_history))
    content.append(Button("Find Another Size", measurements))
    content.append(Button("Back to Home", index))
    return Page(state, content)

@route
def clear_history(state: State)-> Page:
    """clears all saved recommendations from user history and State"""
    state.saved_recommendations = []
    return history(state)

#unit tests
assert_equal(is_valid_number("70.5"), True)
assert_equal(is_valid_number("abc"), False)
assert_equal(calculate_base_size_index(70.0, 170.0, "Gap"), 2)
    
#test index routes
test_state = State(0.0, 0.0, "Regular", "Nike", [])
assert_equal(
    index(test_state),
    Page(
        test_state,
        [
            Header("Shirt Size Finder"),
            "Find the right shirt size across brands based on your body "
            "measurements and fit preference.",
            Button("Get Started", measurements),
            Button("View Saved History", history)]))

#measurement tests
assert_equal(
    measurements(State(0.0, 0.0, "Regular", "Nike", [])),
    Page(
        State(0.0, 0.0, "Regular", "Nike", []),
        [
            Header("Step 1: Your Measurements"),
            "Enter your height (in inches) and weight (in pounds):",
            "Height (inches):",
            TextBox("height_text", ""),
            "Weight (lbs):",
            TextBox("weight_text", ""),
            Button("Next: Fit & Brand", preferences),
            Button("Back to Home", index)]))
       
#preference route test
pref_state = State(0.0, 0.0, "Regular", "Nike", [])
assert_equal(
    preferences(pref_state, "70", "170"),
    Page(
        State(70.0, 170.0, "Regular", "Nike", []),
        [
            Header("Step 2: Fit & Brand Preferences"),
            "Current Measurements: 70.0 in, 170.0 lbs",
            "Preferred Fit:",
            SelectBox("fit", FITS, "Regular"),
            "Clothing Brand:",
            SelectBox("brand", BRANDS, "Nike"),
            Button("Find My Size", recommendation),
            Button("Back to Measurements", measurements)]))

#recommendations route test
rec_state = State(70.0, 170.0, "Regular", "Gap", [])
assert_equal(
    recommendation(rec_state, "Loose", "Gap"),
    Page(
        State(70.0, 170.0, "Loose", "Gap", []),
        [
            Header("Your Recommended Shirt Size"),
            "Brand: Gap",
            "Recommended Size: L",
            "Preferred Fit: Loose",
            "Based on 70.0 in, 170.0 lbs, a Loose fit, and Gap's "
            "sizing chart.",
            Button("Save This Recommendation", save_recommendation),
            Button("View Saved History", history),
            Button("Start Over", index)]))

#test save_recommendation and history route
save_state = State(70.0, 170.0, "Regular", "Gap", [])
expected_rec = ShirtRecommendation(
    "Gap",
    "M",
    "Regular",
    "Based on 70.0 in, 170.0 lbs, a Regular fit, and Gap's sizing chart.",)
assert_equal(
    save_recommendation(save_state),
    Page(State(70.0, 170.0, "Regular", "Gap", [expected_rec]),
        [Header("Saved Shirt Recommendations"),
            "Gap - Size M (Regular fit): Based on 70.0 in, 170.0 lbs, a "
            "Regular fit, and Gap's sizing chart.",
            Button("Clear Saved History", clear_history),
            Button("Find Another Size", measurements),
            Button("Back to Home", index)]))

#test clear_history route

assert_equal(
    clear_history(save_state),
    Page(State(70.0, 170.0, "Regular", "Gap", []),
        [Header("Saved Shirt Recommendations"),
            "You have no saved recommendations yet.",
            Button("Find Another Size", measurements),
            Button("Back to Home", index)]))

start_server(State(0.0, 0.0, "Regular", "Nike", []))
