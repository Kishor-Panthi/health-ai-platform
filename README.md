# HealthCare PM - Practice Management System

A comprehensive, modern healthcare practice management system built with Next.js 16, React 19, and TypeScript. This is a fully functional frontend application with mock data, perfect for demonstrations and prototyping.

## 🎯 Overview

HealthCare PM is a complete practice management solution designed for small to mid-size medical practices. It provides tools for appointment scheduling, patient management, billing, communications, referrals, and analytics—all in a beautiful, responsive interface.

## ✨ Key Features

### 🏥 Core Modules

1. **Dashboard** ([/dashboard](app/dashboard/page.tsx))
   - Today's appointments overview
   - Key metrics widgets (patients, revenue, tasks)
   - Recent activity feed
   - Quick actions
   - Practice health indicators

2. **Appointment Management** ([/dashboard/appointments](app/dashboard/appointments/page.tsx))
   - FullCalendar integration (day/week/month views)
   - Drag-and-drop scheduling
   - Provider filtering
   - Color-coded appointment types
   - Appointment details and status tracking
   - Stats dashboard

3. **Patient Management** ([/dashboard/patients](app/dashboard/patients/page.tsx))
   - Comprehensive patient list with search and filters
   - Detailed patient profiles with tabs:
     - Overview (demographics, contact info, emergency contact)
     - Appointment history
     - Insurance information
     - Documents (placeholder)
   - New patient registration form
   - Patient tags and conditions tracking

4. **Communication Hub** ([/dashboard/communications](app/dashboard/communications/page.tsx))
   - Unified inbox (Email, SMS, Internal, Automated)
   - Message filtering by type
   - Message status tracking (sent, delivered, read, failed)
   - Compose messages with templates
   - Patient selection
   - Communication stats dashboard

5. **Billing & Claims** ([/dashboard/billing](app/dashboard/billing/page.tsx))
   - Claims management dashboard
   - Financial stats (billed, collected, pending, rejected)
   - Claim status tracking
   - Detailed claim views
   - CPT/ICD code reference libraries
   - Insurance payer analytics

6. **Referral Management** ([/dashboard/referrals](app/dashboard/referrals/page.tsx))
   - Kanban board view (Pending, In Progress, Completed, Closed)
   - Priority tracking (Routine, Urgent, STAT)
   - Specialist directory
   - Referral timeline tracking
   - Digital referral forms

7. **Reports & Analytics** ([/dashboard/reports](app/dashboard/reports/page.tsx))
   - Executive dashboard with KPIs
   - Interactive charts (Recharts):
     - Appointment trends and analytics
     - Financial revenue tracking
     - Patient demographics (age/gender distribution)
     - Provider productivity metrics
   - Multiple report categories
   - Export functionality (placeholder)

8. **Settings** ([/dashboard/settings](app/dashboard/settings/page.tsx))
   - 7 comprehensive tabs:
     - Profile settings
     - Practice information and hours
     - Provider and staff management
     - Notification preferences
     - Appearance customization
     - Automation rules
     - Security and HIPAA compliance

### 🚀 Additional Features

- **Authentication System**
  - Mock login/logout functionality
  - User state management with Zustand
  - Route protection middleware
  - Session persistence

- **Command Palette** (Cmd+K / Ctrl+K)
  - Quick navigation to all sections
  - Quick actions (new appointment, new patient, etc.)
  - Keyboard shortcuts

- **Notification System**
  - Real-time notifications dropdown
  - Badge counter for unread items
  - Notification categories (appointments, messages, claims, referrals)
  - Mark as read / mark all as read
  - Persistent storage

- **User Menu**
  - Profile dropdown
  - Quick settings access
  - Logout functionality

## 📊 Mock Data

The system comes with comprehensive mock data:

- **50+ patients** with varied demographics
- **200+ appointments** across 3 months
- **150+ messages** with delivery tracking
- **100+ claims** with financial data
- **30+ referrals** across specialties
- **5 providers** with schedules
- **5 specialists** for referrals
- **4 staff members** with roles
- **CPT/ICD code libraries**
- **Message templates**
- **Automation rules**

## 🛠️ Tech Stack

### Frontend Framework
- **Next.js 16.0.1** with App Router
- **React 19.2.0** (latest)
- **TypeScript 5**

### UI Components
- **shadcn/ui** (Radix UI primitives)
- **Tailwind CSS 3.4.18**
- **Lucide React** (icons)

### State Management
- **Zustand 5.0.8** (with persist middleware)
- **TanStack React Query 5.90.7** (server state)

### Data Visualization
- **Recharts 3.3.0** (charts and graphs)
- **FullCalendar 6.1.19** (calendar views)

### Tables & Forms
- **TanStack React Table 8.21.3**
- **React Hook Form 7.66.0**
- **Zod 4.1.12** (schema validation)

### Additional Libraries
- **date-fns 4.1.0** (date manipulation)
- **react-hot-toast 2.6.0** (notifications)
- **cmdk 1.1.1** (command palette)

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn or pnpm

### Installation

1. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

2. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

3. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Mock Login
- **Email:** Any valid email
- **Password:** Any password (mock authentication)

The system will create a mock user session and redirect you to the dashboard.

## ⌨️ Keyboard Shortcuts

- **Cmd/Ctrl + K** - Open command palette
- **ESC** - Close modals and dropdowns

## 🎨 Design System

### Color Scheme
- **Primary:** Blue (#3b82f6)
- **Success:** Green (#10b981)
- **Warning:** Orange (#f59e0b)
- **Error:** Red (#ef4444)
- **Secondary:** Purple (#8b5cf6)

### Typography
- **Font:** System font stack (sans-serif)
- **Headings:** Bold, tracking-tight
- **Body:** Regular, readable sizes

## 📱 Responsive Design

The application is fully responsive and works on:
- **Desktop:** 1920px+
- **Laptop:** 1024px - 1919px
- **Tablet:** 768px - 1023px
- **Mobile:** 320px - 767px (basic support)

## 🔒 Security Features

- Route protection middleware
- Session management
- User authentication state
- Secure logout
- HIPAA compliance UI indicators

## 📈 Performance Targets

- **Initial Load:** < 3 seconds
- **Page Transitions:** < 200ms
- **Search Results:** < 500ms
- **Calendar Rendering:** < 1 second

## 🎯 Future Enhancements

### Pending Features
- Global search across all entities
- Loading states and skeletons
- Error boundaries
- Dark mode toggle
- Onboarding tour
- Enhanced mobile responsiveness
- Full accessibility (ARIA labels, keyboard nav)
- Testing infrastructure (Jest, Cypress, MSW)
- Storybook component library

### Potential Backend Integration
- Real authentication (NextAuth, Clerk, Supabase)
- Database integration (PostgreSQL, MongoDB)
- API routes
- Real-time updates (WebSockets)
- File upload/management
- Email/SMS integration
- Payment processing
- Reporting exports

## 📄 License

This project is for demonstration purposes. Please ensure compliance with healthcare regulations (HIPAA, etc.) before using in production.

## 🙏 Acknowledgments

- **Next.js Team** - For the amazing framework
- **shadcn** - For the beautiful UI components
- **Vercel** - For hosting and deployment
- **Radix UI** - For accessible primitives
- **Recharts** - For data visualization

---

**Built with ❤️ using Next.js 16, React 19, and TypeScript**
