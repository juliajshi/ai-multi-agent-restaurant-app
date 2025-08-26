# AI Multi-Agent Restaurant Recommendation App

An intelligent restaurant recommendation system powered by multiple AI agents that helps groups find the perfect dining experience based on location fairness, preferences, and budget.

## Architecture

The app uses a **LangGraph** multi-agent workflow with four specialized agents:

1. **Input Agent**: Parses user input to extract member locations, preferences, and budget
2. **Restaurant Agent**: Searches for restaurants using Google Places API based on group preferences
3. **Transportation Agent**: Calculates travel times and fairness scores using Google Distance Matrix API
4. **Output Agent**: Formats final recommendations in a readable table format

## Model Specifications

The application uses Anthropic **Claude Sonnet 4** (claude-sonnet-4-20250514) as the core AI model for all agent operations.

## Prerequisites

- **Python 3.12+**
- **Anthropic API Key** (for Claude AI)
- **Google Maps API Key** (for Places and Distance Matrix APIs)

### Set up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy this into your .env file
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
```

## Installation

### Using UV

```bash
# Clone the repository
git clone <repository-url>
cd ai-multi-agent-restaurant-app

# Install dependencies with UV
uv sync
```

## Usage

### Running the Application

```bash
uv run python main.py
```

### Input Format

Enter your group information in this format:

```
Annie is in Midtown NYC and likes cheap Thai and Indian food. Bob is in East Village and likes Thai and Japanese food. Charlie is in Soho, NYC and likes cheap Mexican food.
```

**Key Components:**

- **Names**: First names of group members
- **Locations**: Specific neighborhoods, addresses, or landmarks
- **Preferences**: Cuisine types and price preferences
- **Budget**: Use terms like "cheap", "moderate", "expensive"

### Example Inputs

```bash
# Example 1: NYC Group
Annie is in Midtown NYC and likes cheap Thai and Indian food. Bob is in East Village and likes Japanese and Thai food. Charlie is in Soho, NYC and likes cheap Mexican food.

# Example 2: San Francisco Group
Sarah is in Mission District, SF and likes moderate Italian food. Mike is in SOMA, SF and likes Asian cuisine. Lisa is in Castro, SF and likes vegetarian Mexican food.
```

### Output

```
+------------------------------------------+--------+----------+-------------+-------+-------+-----+---------+
| Restaurant Name                          | Rating | Reviews  | Cuisine     | Price | Annie | Bob | Charlie |
+------------------------------------------+--------+----------+-------------+-------+-------+-----+---------+
| 7 Elephants                              | 4.8    | 173      | Thai/Asian  | $     | 18    | 9   | 11      |
| https://www.google.com/maps/search/7+Elephants                                                              |
+------------------------------------------+--------+----------+-------------+-------+-------+-----+---------+
| Aroy Dee Thai Kitchen                    | 4.6    | 1,559    | Thai        | $     | 20    | 14  | 7       |
| https://www.google.com/maps/search/Aroy+Dee+Thai+Kitchen                                                    |
+------------------------------------------+--------+----------+-------------+-------+-------+-----+---------+
| Wondee Siam                              | 4.6    | 1,362    | Thai        | $     | 7     | 21  | 20      |
| https://www.google.com/maps/search/Wondee+Siam                                                              |
+------------------------------------------+--------+----------+-------------+-------+-------+-----+---------+

**Rankings by Transportation Score:**
1. **7 Elephants** (75.0) - Best overall travel times and highest rating
2. **Aroy Dee Thai Kitchen** (65.0) - Good balance with most reviews
3. **Wondee Siam** (55.0) - Lowest transportation score but still quality option

All three restaurants offer excellent Thai cuisine at budget-friendly prices ($) that fit your $25 constraint.
```

## Dependencies

- **langchain[anthropic]**: Claude AI integration
- **langgraph**: Multi-agent workflow framework
- **googlemaps**: Google Maps API client
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and parsing
