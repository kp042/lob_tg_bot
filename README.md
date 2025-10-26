# LOB Telegram Bot

A powerful Telegram bot for analyzing Limit Order Book (LOB) data from Binance. This bot provides real-time depth chart visualizations and market data for various cryptocurrency symbols.

## 📊 Features

- **Active Symbols List** - Get all available trading symbols
- **LOB Depth Analysis** - Visualize order book depth for any symbol
- **Multiple Depth Levels** - Analyze 1%, 3%, 5%, and 8% market depth
- **Real-time Charts** - Generate professional depth charts with matplotlib
- **REST API Integration** - Secure JWT authentication with custom API
- **Docker Containerized** - Easy deployment with Docker and Docker Compose

## 🛠 Technologies Used

- **Python 3.11** - Core programming language
- **Aiogram 3.3** - Modern asynchronous Telegram Bot Framework
- **Pandas & Matplotlib** - Data analysis and chart generation
- **Aiohttp** - Asynchronous HTTP client for API calls
- **Docker** - Containerization for easy deployment
- **Pydantic Settings** - Environment configuration management

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- API credentials for LOB data service

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lob-tg-bot.git
   cd lob-tg-bot
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Update .env file**
   ```env
   TG_BOT_TOKEN=your_telegram_bot_token_here
   API_BASE=your_api_base_url
   API_USER=your_api_username
   API_PASS=your_api_password
   ```

4. **Build and start the container**
   ```bash
   docker compose up -d
   ```

5. **Check logs**
   ```bash
   docker compose logs -f lob-tg-bot
   ```

## 📁 Project Structure

```
lob_tg_bot/
├── app/
│   ├── main.py                 # Bot entry point
│   ├── core/
│   │   ├── app_context.py      # Application context
│   │   └── config.py           # Configuration management
│   ├── handlers/
│   │   ├── lob.py              # LOB analysis commands
│   │   └── user.py             # Basic user commands
│   ├── lexicon/
│   │   └── lexicon.py          # Bot messages and menus
│   └── services/
│       ├── api_client.py       # API client with JWT auth
│       ├── lob_data.py         # LOB data processing
│       ├── msg_manager.py      # Message sending utilities
│       └── utils.py            # Chart generation and utilities
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Service orchestration
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## 🤖 Bot Commands

- `/start` - Welcome message and bot description
- `/help` - List of available commands with descriptions
- `/symbols` - Get all active trading symbols
- `/check_lob_by_symbol` - Analyze LOB depth for a specific symbol

## 📈 Chart Types

The bot generates professional depth charts showing:

1. **Best Bid/Ask Prices** - Real-time price movements
2. **Market Depth** - Volume at different price levels (1%, 3%, 5%, 8%)
3. **Dark Theme** - Optimized for comfortable viewing

## 🔧 API Integration

The bot integrates with a custom REST API featuring:

- **JWT Authentication** - Secure token-based authentication
- **Real-time LOB Data** - Live order book data from Binance
- **Symbol Management** - Dynamic symbol listing
- **Rate Limiting** - Proper request throttling

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and start
docker compose up -d --build

# Stop services
docker compose down

# View logs
docker compose logs -f lob-tg-bot

# Restart services
docker compose restart lob-tg-bot
```

### Development

```bash
# Build with no cache
docker compose build --no-cache

# Run with logs
docker compose up

# Enter container for debugging
docker exec -it lob_tg_bot /bin/bash
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TG_BOT_TOKEN` | Telegram Bot API token | Yes |
| `API_BASE` | Base URL for LOB data API | Yes |
| `API_USER` | API authentication username | Yes |
| `API_PASS` | API authentication password | Yes |

### Docker Volumes

- `app_images` - Temporary chart images
- Container logs are handled via Docker's logging driver

## 🔒 Security Features

- Non-root user execution in Docker
- JWT token authentication with automatic renewal
- Environment variable configuration
- Secure API client with proper error handling

## 📊 Performance

- **Asynchronous Processing** - All I/O operations are non-blocking
- **Efficient Chart Generation** - Matplotlib with Agg backend for server-side rendering
- **Memory Management** - Automatic cleanup of temporary files
- **Optimized Docker Image** - Multi-stage build with minimal layers

## 🐛 Troubleshooting

### Common Issues

1. **Permission denied errors**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Module import errors**
   ```bash
   docker compose build --no-cache
   ```

3. **API connection issues**
   - Verify API credentials in `.env`
   - Check network connectivity to API server

### Logs and Monitoring

```bash
# Real-time logs
docker compose logs -f lob-tg-bot

# Last 100 lines
docker compose logs --tail=100 lob-tg-bot

# Logs with timestamps
docker compose logs -t lob-tg-bot
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Aiogram](https://github.com/aiogram/aiogram) for the excellent Telegram Bot framework
- [Binance](https://www.binance.com/) for market data
- [Matplotlib](https://matplotlib.org/) for chart generation
- [Docker](https://www.docker.com/) for containerization

---

**Note**: This bot requires access to a proprietary LOB data API. The API client is designed to work with custom backend services providing real-time cryptocurrency market data.

For questions and support, please open an issue in the GitHub repository.
