# KAEL Ultimate Dashboard

> Professional, real-time dashboard for monitoring the KAEL Ultimate Strategy Evaluator

## Features

### UI/UX Excellence
- ✅ **Modern, Responsive Design**: Works seamlessly across desktop, tablet, and mobile
- ✅ **Dark/Light Mode**: Eye-friendly themes with smooth transitions
- ✅ **Real-time Updates**: Auto-refresh every 5 seconds with visual indicators
- ✅ **Interactive Components**: Sortable tables, hover effects, and smooth animations
- ✅ **Professional Color Scheme**: Carefully chosen colors for clarity and accessibility

### Key Functionality
- 📊 **Portfolio Overview**: Real-time balance, P&L, ROI, and drawdown metrics
- 📈 **Strategy Performance**: Detailed comparison of all 7 strategies
- 📉 **Interactive Charts**: Bar charts showing win rates, P&L, and Sharpe ratios
- 📑 **Data Export**: Export to Excel, PDF, CSV, and JSON
- 🎯 **KPI Cards**: At-a-glance view of critical metrics
- 🔄 **Auto-Refresh**: Configurable refresh intervals

### Technical Stack
- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast

## Quick Start

### Development Mode

1. **Install dependencies**:
   ```bash
   cd dashboard-ui-react
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open browser**:
   ```
   http://localhost:3000
   ```

### Production Build

```bash
npm run build
npm run preview
```

## Docker Deployment

### Using Docker Compose (Recommended)

From the project root:

```bash
# Build and start all services
docker-compose -f docker-compose.ultimate-evaluator.yml up -d --build

# View logs
docker-compose -f docker-compose.ultimate-evaluator.yml logs -f dashboard

# Stop services
docker-compose -f docker-compose.ultimate-evaluator.yml down
```

### Standalone Docker Build

```bash
cd dashboard-ui-react
docker build -t kael-dashboard .
docker run -p 3000:80 kael-dashboard
```

## API Integration

The dashboard connects to the Ultimate Strategy Evaluator API at `http://localhost:5001`.

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/statistics` | GET | Portfolio and strategy metrics |
| `/strategies` | GET | All strategies summary |
| `/strategy/{name}` | GET | Specific strategy details |
| `/export/csv` | GET | Export trades to CSV |
| `/export/json` | GET | Export performance to JSON |
| `/metrics` | GET | Prometheus metrics |

### Data Structure

```typescript
interface PortfolioStats {
  initial_balance: number;
  current_balance: number;
  daily_pnl: number;
  roi: number;
  max_drawdown: number;
  total_trades: number;
  total_wins: number;
  total_losses: number;
  portfolio_win_rate: number;
  active_strategies: number;
  strategies: Record<string, StrategyMetrics>;
}

interface StrategyMetrics {
  strategy_name: string;
  total_trades: number;
  wins: number;
  losses: number;
  win_rate: number;
  total_pnl: number;
  avg_confidence: number;
  sharpe_ratio: number;
  kelly_fraction: number;
  current_streak: number;
}
```

## Configuration

### Environment Variables

Create `.env` file:

```bash
# API Configuration
VITE_API_URL=http://localhost:5001
```

### Customize Auto-Refresh

Edit `src/App.tsx`:

```typescript
const { data, loading, error, refetch } = usePortfolioStats(
  true,    // autoRefresh: true/false
  5000     // refreshInterval: milliseconds
);
```

## Features in Detail

### KPI Cards
- Real-time portfolio metrics with trend indicators
- Color-coded values (green for positive, red for negative)
- Subtitle information for context
- Hover effects for interactivity

### Strategy Table
- **Sortable columns**: Click column headers to sort
- **Color-coded win rates**:
  - Green: ≥60%
  - Yellow: 50-59%
  - Red: <50%
- **Current streak indicators**: Shows consecutive wins/losses
- **Hover highlighting**: Better row visibility

### Performance Chart
- **Multi-metric visualization**: Win rate, P&L, and Sharpe ratio
- **Interactive tooltips**: Detailed info on hover
- **Responsive design**: Adjusts to screen size
- **Professional aesthetics**: Rounded bars, proper spacing

### Export Functionality
- **Excel**: Comprehensive workbook with multiple sheets
- **PDF**: Professional report with tables and charts
- **CSV**: Raw trade data from backend
- **JSON**: Structured performance data

### Theme System
- **Dark mode default**: Eye-friendly for long sessions
- **Light mode option**: For bright environments
- **Smooth transitions**: Animated theme changes
- **Persistent selection**: Saved in localStorage

## Project Structure

```
dashboard-ui-react/
├── src/
│   ├── components/        # React components
│   │   ├── Header.tsx    # Top navigation bar
│   │   ├── KPICard.tsx   # Metric display cards
│   │   ├── StrategyTable.tsx  # Strategy comparison table
│   │   └── PerformanceChart.tsx  # Interactive charts
│   ├── hooks/            # Custom React hooks
│   │   ├── usePortfolioStats.ts  # Data fetching
│   │   └── useTheme.ts  # Theme management
│   ├── services/         # API integration
│   │   └── api.ts       # API client
│   ├── types/            # TypeScript definitions
│   │   └── api.ts       # API types
│   ├── utils/            # Utility functions
│   │   ├── format.ts    # Formatting helpers
│   │   └── export.ts    # Export functions
│   ├── App.tsx           # Main application
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── Dockerfile            # Production container
├── nginx.conf            # Nginx configuration
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # TailwindCSS configuration
└── package.json          # Dependencies

```

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- **Initial Load**: <2 seconds
- **First Contentful Paint**: <1 second
- **Time to Interactive**: <2.5 seconds
- **Bundle Size**: ~200KB (gzipped)

## Troubleshooting

### Dashboard not loading

1. Check if evaluator is running:
   ```bash
   curl http://localhost:5001/health
   ```

2. Check Docker logs:
   ```bash
   docker logs kael-dashboard
   ```

### API connection errors

1. Verify API URL in `.env`
2. Check network connectivity
3. Ensure evaluator is healthy:
   ```bash
   docker ps | grep kael-ultimate-evaluator
   ```

### Build errors

1. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Clear Vite cache:
   ```bash
   rm -rf node_modules/.vite
   ```

## Development

### Adding New Features

1. **New Component**:
   ```typescript
   // src/components/MyComponent.tsx
   export function MyComponent() {
     return <div>Hello</div>;
   }
   ```

2. **New Hook**:
   ```typescript
   // src/hooks/useMyHook.ts
   export function useMyHook() {
     // Hook logic
   }
   ```

3. **New Utility**:
   ```typescript
   // src/utils/myUtil.ts
   export function myUtil() {
     // Utility logic
   }
   ```

### Code Style

- Use TypeScript for type safety
- Follow React hooks best practices
- Use Tailwind for styling
- Keep components small and focused
- Write self-documenting code

## Future Enhancements

- [ ] WebSocket for real-time updates
- [ ] Historical performance charts
- [ ] Strategy comparison filters
- [ ] Customizable dashboard layouts
- [ ] Multi-user support with authentication
- [ ] Push notifications for alerts
- [ ] Mobile app (React Native)
- [ ] Advanced analytics and predictions

## License

Proprietary - KAEL Trading System

## Support

For issues or questions:
1. Check this README
2. Review the Ultimate Strategy Evaluator documentation
3. Check Docker logs
4. Contact the development team

---

**Version**: 1.0.0
**Last Updated**: 2025-01-28
**Author**: KAEL Development Team
