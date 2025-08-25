# AI Multi-Agent Restaurant Recommendation App 🍽️

An intelligent restaurant recommendation system powered by multiple AI agents that helps groups find the perfect dining experience based on location fairness, preferences, and budget.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for input processing, restaurant search, transportation analysis, and output formatting
- **Location-Based Search**: Uses Google Places API to find restaurants near your group
- **Transportation Fairness**: Calculates travel times and fairness scores using Google Distance Matrix API
- **Smart Recommendations**: Considers dietary preferences, budget constraints, and location equity
- **Real-time Data**: Live restaurant information including ratings, reviews, and current status

## 🏗️ Architecture

The app uses a **LangGraph** multi-agent workflow with four specialized agents:

1. **Input Agent**: Parses user input to extract member locations, preferences, and budget
2. **Restaurant Agent**: Searches for restaurants using Google Places API based on group preferences
3. **Transportation Agent**: Calculates travel times and fairness scores using Google Distance Matrix API
4. **Output Agent**: Formats final recommendations in a readable table format

## 📋 Prerequisites

- **Python 3.12+**
- **Anthropic API Key** (for Claude AI)
- **Google Maps API Key** (for Places and Distance Matrix APIs)

## 🔑 API Key Setup

### 1. Get an Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create Key"**
5. Give your key a name (e.g., "Restaurant App")
6. Copy the generated API key (starts with `sk-ant-`)

### 2. Get a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Places API (New)**
   - **Distance Matrix API**
   - **Geocoding API**
4. Navigate to **APIs & Services > Credentials**
5. Click **"Create Credentials" > "API Key"**
6. Copy the generated API key
7. **(Recommended)** Restrict the API key to only the required APIs for security

### 3. Set up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy this into your .env file
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
```

**Important**: Never commit your `.env` file to version control!

## 🛠️ Installation

### Using UV

```bash
# Clone the repository
git clone <repository-url>
cd ai-multiagent-restaurant-app

# Install dependencies with UV
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows
```

## 🎯 Usage

### Running the Application

```bash
uv run python main.py
```

### Use Case

Use this to help plan where to meet with your friends for dinner.

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

# Example 3: With Transportation Preferences
John is in Downtown LA and likes expensive steakhouses and will drive. Emma is in Santa Monica and likes moderate seafood and prefers public transit.
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

## 🔧 Dependencies

- **langchain[anthropic]**: Claude AI integration
- **langgraph**: Multi-agent workflow framework
- **googlemaps**: Google Maps API client
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and parsing
