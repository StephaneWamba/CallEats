# Restaurant Voice Assistant - Frontend

React + TypeScript frontend application for the Restaurant Voice Assistant platform.

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (default: `http://localhost:8000`)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Set up environment variables:

```bash
cp .env.example .env.local
```

Edit `.env.local` and set your API base URL:

```
VITE_API_BASE_URL=http://localhost:8000
```

For production, use your Railway deployment URL:

```
VITE_API_BASE_URL=https://your-app-name.railway.app
```

3. Start development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## 📁 Project Structure

```
src/
├── api/              # API client and endpoints
├── components/        # React components
│   ├── common/       # Reusable components
│   ├── layout/       # Layout components
│   ├── auth/         # Authentication components
│   └── ...
├── pages/            # Page components
├── hooks/            # Custom React hooks
├── store/            # Redux store and slices
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
├── config/           # Configuration files
└── styles/           # Global styles
```

## 🛠️ Technology Stack

- **React 18** with TypeScript
- **Vite** for building
- **Redux Toolkit** for state management
- **React Query** for server state
- **React Router v6** for routing
- **Tailwind CSS** for styling
- **React Hook Form + Zod** for forms
- **Axios** for HTTP client

## 📚 Key Features

- ✅ Authentication (Login, Sign Up, Password Reset)
- ✅ Dashboard with statistics
- ✅ Menu Builder (Categories, Items, Modifiers)
- ✅ Operating Hours Management
- ✅ Delivery Zones with Map Integration
- ✅ Call History
- ✅ Settings

## 🔗 API Integration

The frontend connects to the backend API. Make sure the backend is running and the `VITE_API_BASE_URL` is correctly configured.

All API endpoints are defined in `src/config/env.ts` and match the backend routes exactly.

## 📱 Responsive Design

The application is fully responsive with breakpoints:

- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

## 🧪 Development

- Run dev server: `npm run dev`
- Build: `npm run build`
- Preview build: `npm run preview`

## 📖 Documentation

See the `backend/private/` directory for detailed documentation:

- `frontend_architecture.md` - Architecture and best practices
- `mobile_responsive_design.md` - Responsive design guidelines
- `frontend_implementation_roadmap.md` - Implementation roadmap
- `backend_frontend_assessment.md` - API endpoint documentation
