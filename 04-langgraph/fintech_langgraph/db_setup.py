import sqlite3
from datetime import datetime, timedelta
import random

def create_database():
    conn = sqlite3.connect('fintech.db')
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        email TEXT UNIQUE,
        name TEXT,
        created_at TIMESTAMP,
        risk_profile TEXT,
        investment_goals TEXT,
        is_admin BOOLEAN DEFAULT 0
    )''')

    # Create Portfolios table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolios (
        portfolio_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        created_at TIMESTAMP,
        total_value DECIMAL(10,2),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )''')

    # Create Stocks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks (
        symbol TEXT PRIMARY KEY,
        name TEXT,
        sector TEXT,
        industry TEXT,
        current_price DECIMAL(10,2),
        last_updated TIMESTAMP
    )''')

    # Create Portfolio Holdings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio_holdings (
        holding_id INTEGER PRIMARY KEY,
        portfolio_id INTEGER,
        symbol TEXT,
        quantity INTEGER,
        average_cost DECIMAL(10,2),
        current_value DECIMAL(10,2),
        last_updated TIMESTAMP,
        FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id),
        FOREIGN KEY (symbol) REFERENCES stocks(symbol)
    )''')

    # Create Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        portfolio_id INTEGER,
        symbol TEXT,
        transaction_type TEXT,
        quantity INTEGER,
        price DECIMAL(10,2),
        transaction_date TIMESTAMP,
        FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id),
        FOREIGN KEY (symbol) REFERENCES stocks(symbol)
    )''')

    # Create Market News table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS market_news (
        news_id INTEGER PRIMARY KEY,
        symbol TEXT,
        title TEXT,
        content TEXT,
        published_date TIMESTAMP,
        sentiment TEXT,
        FOREIGN KEY (symbol) REFERENCES stocks(symbol)
    )''')

    conn.commit()
    conn.close()

def insert_sample_data():
    conn = sqlite3.connect('fintech.db')
    cursor = conn.cursor()

    # Clear existing data
    tables = ['users', 'portfolios', 'stocks', 'portfolio_holdings', 
              'transactions', 'market_news']
    for table in tables:
        cursor.execute(f'DELETE FROM {table}')

    # Insert sample users (15 users)
    users = [
        (1, 'admin@fintech.com', 'Admin User', '2024-01-01', 'Moderate', 'Long-term Growth', 1),
        (2, 'john.doe@email.com', 'John Doe', '2024-01-01', 'Moderate', 'Long-term Growth', 0),
        (3, 'jane.smith@email.com', 'Jane Smith', '2024-01-15', 'Conservative', 'Income', 0),
        (4, 'bob.wilson@email.com', 'Bob Wilson', '2024-02-01', 'Aggressive', 'Capital Appreciation', 0),
        (5, 'sarah.jones@email.com', 'Sarah Jones', '2024-02-15', 'Conservative', 'Retirement', 0),
        (6, 'mike.brown@email.com', 'Mike Brown', '2024-03-01', 'Moderate', 'Education Fund', 0),
        (7, 'emma.davis@email.com', 'Emma Davis', '2024-03-15', 'Aggressive', 'Wealth Building', 0),
        (8, 'david.miller@email.com', 'David Miller', '2024-04-01', 'Conservative', 'Emergency Fund', 0),
        (9, 'lisa.wilson@email.com', 'Lisa Wilson', '2024-04-15', 'Moderate', 'Home Purchase', 0),
        (10, 'tom.harris@email.com', 'Tom Harris', '2024-05-01', 'Aggressive', 'Early Retirement', 0),
        (11, 'anna.clark@email.com', 'Anna Clark', '2024-05-15', 'Conservative', 'Tax Planning', 0),
        (12, 'peter.lee@email.com', 'Peter Lee', '2024-06-01', 'Moderate', 'Diversification', 0),
        (13, 'mary.taylor@email.com', 'Mary Taylor', '2024-06-15', 'Aggressive', 'High Growth', 0),
        (14, 'james.martin@email.com', 'James Martin', '2024-07-01', 'Conservative', 'Stable Income', 0),
        (15, 'sophie.anderson@email.com', 'Sophie Anderson', '2024-07-15', 'Moderate', 'Balanced Growth', 0)
    ]
    cursor.executemany('INSERT INTO users VALUES (?,?,?,?,?,?,?)', users)

    # Insert sample stocks (20 stocks)
    stocks = [
        ('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 175.50, '2024-03-15'),
        ('MSFT', 'Microsoft Corp.', 'Technology', 'Software', 380.25, '2024-03-15'),
        ('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Services', 142.75, '2024-03-15'),
        ('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 'Internet Retail', 175.35, '2024-03-15'),
        ('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 175.50, '2024-03-15'),
        ('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 'Banks', 180.25, '2024-03-15'),
        ('V', 'Visa Inc.', 'Financial Services', 'Credit Services', 275.75, '2024-03-15'),
        ('WMT', 'Walmart Inc.', 'Consumer Defensive', 'Discount Stores', 60.35, '2024-03-15'),
        ('JNJ', 'Johnson & Johnson', 'Healthcare', 'Pharmaceuticals', 155.80, '2024-03-15'),
        ('PG', 'Procter & Gamble', 'Consumer Defensive', 'Household Products', 160.45, '2024-03-15'),
        ('HD', 'Home Depot Inc.', 'Consumer Cyclical', 'Home Improvement', 375.20, '2024-03-15'),
        ('BAC', 'Bank of America', 'Financial Services', 'Banks', 35.75, '2024-03-15'),
        ('KO', 'Coca-Cola Co.', 'Consumer Defensive', 'Beverages', 60.25, '2024-03-15'),
        ('DIS', 'Walt Disney Co.', 'Communication Services', 'Entertainment', 110.50, '2024-03-15'),
        ('NFLX', 'Netflix Inc.', 'Communication Services', 'Entertainment', 580.75, '2024-03-15'),
        ('NVDA', 'NVIDIA Corp.', 'Technology', 'Semiconductors', 875.25, '2024-03-15'),
        ('META', 'Meta Platforms Inc.', 'Technology', 'Internet Services', 485.50, '2024-03-15'),
        ('PYPL', 'PayPal Holdings', 'Financial Services', 'Credit Services', 65.80, '2024-03-15'),
        ('INTC', 'Intel Corp.', 'Technology', 'Semiconductors', 42.15, '2024-03-15'),
        ('CSCO', 'Cisco Systems', 'Technology', 'Networking', 48.90, '2024-03-15')
    ]
    cursor.executemany('INSERT INTO stocks VALUES (?,?,?,?,?,?)', stocks)

    # Insert sample portfolios (20 portfolios)
    portfolios = [
        (1, 2, 'Main Portfolio', '2024-01-01', 50000.00),
        (2, 2, 'Tech Portfolio', '2024-01-15', 25000.00),
        (3, 3, 'Retirement Portfolio', '2024-01-15', 100000.00),
        (4, 4, 'Growth Portfolio', '2024-02-01', 75000.00),
        (5, 5, 'Conservative Portfolio', '2024-02-15', 60000.00),
        (6, 6, 'Education Fund', '2024-03-01', 30000.00),
        (7, 7, 'High Growth Portfolio', '2024-03-15', 120000.00),
        (8, 8, 'Emergency Fund', '2024-04-01', 25000.00),
        (9, 9, 'Home Purchase Fund', '2024-04-15', 80000.00),
        (10, 10, 'Early Retirement', '2024-05-01', 200000.00),
        (11, 11, 'Tax Planning', '2024-05-15', 45000.00),
        (12, 12, 'Diversified Portfolio', '2024-06-01', 90000.00),
        (13, 13, 'Aggressive Growth', '2024-06-15', 150000.00),
        (14, 14, 'Income Portfolio', '2024-07-01', 70000.00),
        (15, 15, 'Balanced Growth', '2024-07-15', 85000.00),
        (16, 2, 'Dividend Portfolio', '2024-08-01', 40000.00),
        (17, 3, 'Tech Growth', '2024-08-15', 55000.00),
        (18, 4, 'Value Portfolio', '2024-09-01', 65000.00),
        (19, 5, 'Blue Chip Portfolio', '2024-09-15', 95000.00),
        (20, 6, 'Small Cap Growth', '2024-10-01', 35000.00)
    ]
    cursor.executemany('INSERT INTO portfolios VALUES (?,?,?,?,?)', portfolios)

    # Insert sample portfolio holdings (40 holdings)
    holdings = [
        (1, 1, 'AAPL', 100, 150.00, 17550.00, '2024-03-15'),
        (2, 1, 'MSFT', 50, 350.00, 19012.50, '2024-03-15'),
        (3, 2, 'GOOGL', 75, 140.00, 10706.25, '2024-03-15'),
        (4, 2, 'AMZN', 25, 170.00, 4383.75, '2024-03-15'),
        (5, 3, 'JPM', 200, 175.00, 36050.00, '2024-03-15'),
        (6, 3, 'V', 100, 270.00, 27575.00, '2024-03-15'),
        (7, 4, 'TSLA', 150, 180.00, 26325.00, '2024-03-15'),
        (8, 4, 'WMT', 300, 55.00, 18105.00, '2024-03-15'),
        (9, 5, 'JNJ', 200, 150.00, 31160.00, '2024-03-15'),
        (10, 5, 'PG', 150, 155.00, 24067.50, '2024-03-15'),
        (11, 6, 'HD', 50, 360.00, 18760.00, '2024-03-15'),
        (12, 6, 'BAC', 500, 34.00, 17875.00, '2024-03-15'),
        (13, 7, 'NVDA', 20, 800.00, 17505.00, '2024-03-15'),
        (14, 7, 'META', 30, 450.00, 14565.00, '2024-03-15'),
        (15, 8, 'KO', 200, 58.00, 12050.00, '2024-03-15'),
        (16, 8, 'DIS', 100, 105.00, 11050.00, '2024-03-15'),
        (17, 9, 'NFLX', 20, 550.00, 11615.00, '2024-03-15'),
        (18, 9, 'PYPL', 150, 60.00, 9870.00, '2024-03-15'),
        (19, 10, 'INTC', 300, 40.00, 12645.00, '2024-03-15'),
        (20, 10, 'CSCO', 200, 45.00, 9780.00, '2024-03-15'),
        (21, 11, 'AAPL', 50, 150.00, 8775.00, '2024-03-15'),
        (22, 11, 'MSFT', 25, 350.00, 9506.25, '2024-03-15'),
        (23, 12, 'GOOGL', 40, 140.00, 5710.00, '2024-03-15'),
        (24, 12, 'AMZN', 15, 170.00, 2630.25, '2024-03-15'),
        (25, 13, 'TSLA', 80, 180.00, 14040.00, '2024-03-15'),
        (26, 13, 'NVDA', 15, 800.00, 13128.75, '2024-03-15'),
        (27, 14, 'JNJ', 100, 150.00, 15580.00, '2024-03-15'),
        (28, 14, 'PG', 75, 155.00, 12033.75, '2024-03-15'),
        (29, 15, 'HD', 30, 360.00, 11256.00, '2024-03-15'),
        (30, 15, 'BAC', 300, 34.00, 10725.00, '2024-03-15'),
        (31, 16, 'V', 50, 270.00, 13787.50, '2024-03-15'),
        (32, 16, 'JPM', 100, 175.00, 18025.00, '2024-03-15'),
        (33, 17, 'AAPL', 30, 150.00, 5265.00, '2024-03-15'),
        (34, 17, 'MSFT', 15, 350.00, 5703.75, '2024-03-15'),
        (35, 18, 'WMT', 200, 55.00, 12070.00, '2024-03-15'),
        (36, 18, 'KO', 100, 58.00, 6025.00, '2024-03-15'),
        (37, 19, 'JNJ', 150, 150.00, 23370.00, '2024-03-15'),
        (38, 19, 'PG', 100, 155.00, 16045.00, '2024-03-15'),
        (39, 20, 'NVDA', 10, 800.00, 8752.50, '2024-03-15'),
        (40, 20, 'META', 20, 450.00, 9710.00, '2024-03-15')
    ]
    cursor.executemany('INSERT INTO portfolio_holdings VALUES (?,?,?,?,?,?,?)', holdings)

    # Insert sample transactions (100 transactions)
    transactions = []
    symbols = [stock[0] for stock in stocks]
    for day in range(30):
        date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
        for _ in range(3):  # 3-4 random transactions per day
            portfolio_id = random.randint(1, 20)
            symbol = random.choice(symbols)
            transaction_type = random.choice(['BUY', 'SELL'])
            quantity = random.randint(1, 100)
            price = random.uniform(30, 900)
            transactions.append((None, portfolio_id, symbol, transaction_type, quantity, price, date))

    cursor.executemany('INSERT INTO transactions VALUES (?,?,?,?,?,?,?)', transactions)

    # Insert sample market news (30 news items)
    news = [
        (1, 'AAPL', 'Apple Announces New iPhone', 'Apple Inc. has announced its latest iPhone model with advanced AI features...', '2024-03-15', 'Positive'),
        (2, 'MSFT', 'Microsoft Cloud Growth', 'Microsoft reports strong cloud growth exceeding market expectations...', '2024-03-14', 'Positive'),
        (3, 'GOOGL', 'Google AI Breakthrough', 'Google announces major AI breakthrough in natural language processing...', '2024-03-13', 'Positive'),
        (4, 'AMZN', 'Amazon Expands Operations', 'Amazon plans to expand its operations to three new countries...', '2024-03-12', 'Neutral'),
        (5, 'TSLA', 'Tesla Production Issues', 'Tesla faces production challenges at its new factory...', '2024-03-11', 'Negative'),
        (6, 'JPM', 'JPMorgan Q1 Results', 'JPMorgan reports strong Q1 earnings despite market volatility...', '2024-03-10', 'Positive'),
        (7, 'V', 'Visa Digital Payment Growth', 'Visa reports record growth in digital payment transactions...', '2024-03-09', 'Positive'),
        (8, 'WMT', 'Walmart Expands E-commerce', 'Walmart announces major expansion of its e-commerce platform...', '2024-03-08', 'Positive'),
        (9, 'JNJ', 'Johnson & Johnson Innovation', 'Johnson & Johnson announces breakthrough in medical research...', '2024-03-07', 'Positive'),
        (10, 'PG', 'P&G Product Launch', 'Procter & Gamble launches new sustainable product line...', '2024-03-06', 'Positive'),
        (11, 'HD', 'Home Depot Expansion', 'Home Depot plans to open 50 new stores...', '2024-03-05', 'Positive'),
        (12, 'BAC', 'Bank of America Strategy', 'Bank of America announces new digital banking strategy...', '2024-03-04', 'Neutral'),
        (13, 'KO', 'Coca-Cola Sustainability', 'Coca-Cola commits to 100% recyclable packaging...', '2024-03-03', 'Positive'),
        (14, 'DIS', 'Disney Streaming Success', 'Disney+ reports subscriber growth above expectations...', '2024-03-02', 'Positive'),
        (15, 'NFLX', 'Netflix Content Strategy', 'Netflix announces major content investment...', '2024-03-01', 'Positive'),
        (16, 'NVDA', 'NVIDIA AI Leadership', 'NVIDIA maintains leadership in AI chip market...', '2024-02-29', 'Positive'),
        (17, 'META', 'Meta Platform Changes', 'Meta announces new privacy features...', '2024-02-28', 'Neutral'),
        (18, 'PYPL', 'PayPal Partnership', 'PayPal forms strategic partnership with major retailer...', '2024-02-27', 'Positive'),
        (19, 'INTC', 'Intel Manufacturing', 'Intel faces delays in new chip production...', '2024-02-26', 'Negative'),
        (20, 'CSCO', 'Cisco Security Solution', 'Cisco launches new cybersecurity platform...', '2024-02-25', 'Positive'),
        (21, 'AAPL', 'Apple Services Growth', 'Apple reports strong growth in services revenue...', '2024-02-24', 'Positive'),
        (22, 'MSFT', 'Microsoft AI Investment', 'Microsoft increases investment in AI research...', '2024-02-23', 'Positive'),
        (23, 'GOOGL', 'Google Search Update', 'Google announces major search algorithm update...', '2024-02-22', 'Neutral'),
        (24, 'AMZN', 'Amazon Cloud Services', 'Amazon Web Services expands global infrastructure...', '2024-02-21', 'Positive'),
        (25, 'TSLA', 'Tesla Battery Technology', 'Tesla announces breakthrough in battery technology...', '2024-02-20', 'Positive'),
        (26, 'JPM', 'JPMorgan Digital Banking', 'JPMorgan enhances digital banking platform...', '2024-02-19', 'Positive'),
        (27, 'V', 'Visa Security Update', 'Visa implements new security measures...', '2024-02-18', 'Neutral'),
        (28, 'WMT', 'Walmart Sustainability', 'Walmart sets new sustainability goals...', '2024-02-17', 'Positive'),
        (29, 'JNJ', 'Johnson & Johnson Vaccine', 'Johnson & Johnson receives regulatory approval...', '2024-02-16', 'Positive'),
        (30, 'PG', 'P&G Market Share', 'Procter & Gamble gains market share in key categories...', '2024-02-15', 'Positive')
    ]
    cursor.executemany('INSERT INTO market_news VALUES (?,?,?,?,?,?)', news)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    insert_sample_data()
    print("Database created and populated with sample data successfully!") 