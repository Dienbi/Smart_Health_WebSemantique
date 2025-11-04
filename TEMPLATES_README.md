# Smart Health Web Templates

## Overview

Beautiful, modern, and responsive healthcare templates for the Smart Health application with blue and white theme inspired by medical aesthetics.

## Templates Created

### 1. Base Template (`base.html`)

- **Purpose**: Main layout template with navigation and footer
- **Features**:
  - Responsive Bootstrap 5 navbar with gradient blue design
  - Dynamic navigation based on user authentication status
  - Footer with social links and company information
  - Smooth animations and hover effects
  - Mobile-friendly responsive design

### 2. Home Page (`home.html`)

- **Purpose**: Landing page for visitors and logged-in users
- **Sections**:
  - **Hero Section**: Eye-catching introduction with statistics
  - **Features Section**: 6 key features with animated cards
  - **About Section**: Information about Smart Health platform
  - **CTA Section**: Call-to-action for signup/AI assistant
- **Features**:
  - Animated elements on scroll
  - SVG illustrations with gradient colors
  - Responsive grid layout
  - Smooth scroll for anchor links

### 3. Login Page (`login.html`)

- **Purpose**: User authentication page
- **Features**:
  - Two-column layout (info + form)
  - Left side with gradient background and benefits
  - Right side with login form
  - Remember me checkbox
  - Forgot password link
  - Social login buttons (Google, Facebook)
  - Password visibility toggle
  - Link to signup page

### 4. Signup Page (`signup.html`)

- **Purpose**: User registration page
- **Features**:
  - Two-column layout matching login design
  - User type selector (Student/Teacher)
  - Form fields:
    - First Name & Last Name
    - Username
    - Email
    - Password & Confirm Password
  - Terms & conditions checkbox
  - Password visibility toggle
  - Link to login page
  - Responsive design

### 5. Admin Dashboard (`dashboard.html`)

- **Purpose**: Admin control panel for managing the platform
- **Features**:
  - **Dashboard Header**: Welcome message with current date
  - **Statistics Cards**: 4 key metrics with trend indicators
    - Total Users
    - Activities Logged
    - Meals Tracked
    - Health Records
  - **Quick Actions**: 6 shortcut buttons
    - Django Admin
    - AI Assistant
    - Fuseki Server
    - Analytics
    - User Management
    - Settings
  - **Recent Users Table**: Latest registered users
  - **Activity Feed**: Recent platform activities
  - **System Status**: Monitor service health
  - Auto-refresh every 5 minutes
  - Animated card entrance

## URL Routes

```python
# Authentication
/                  # Home page
/login/            # Login page
/signup/           # Signup page
/logout/           # Logout (redirects to home)
/dashboard/        # Admin dashboard (staff only)

# API
/api/ai/query/     # AI query endpoint
/api/ai/test/      # AI test interface
```

## Authentication Flow

### For Regular Users:

1. Visit home page
2. Click "Login / Sign Up"
3. Login or create account
4. Redirected to home page (with access to AI features)

### For Admin Users:

1. Visit home page or /admin
2. Login with admin credentials
3. Automatically redirected to `/dashboard/`
4. Access to all admin features

## Color Scheme

```css
--primary-blue: #1e88e5; /* Main blue */
--secondary-blue: #0d47a1; /* Dark blue */
--light-blue: #e3f2fd; /* Light blue background */
--accent-blue: #42a5f5; /* Accent blue */
--white: #ffffff; /* White */
--light-gray: #f5f7fa; /* Light gray background */
--text-dark: #2c3e50; /* Dark text */
--text-light: #7f8c8d; /* Light text */
```

## Typography

- **Font Family**: Poppins (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

## Icons

- **Bootstrap Icons** v1.11.0
- Categories used:
  - Health: heart-pulse, activity, egg-fried
  - UI: person, lock, envelope, eye, gear
  - Actions: check-circle, arrow-right, plus
  - Social: facebook, google, twitter, instagram

## Responsive Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 992px
- **Desktop**: > 992px

## Features

### Animations

- Fade in up on scroll
- Hover effects on cards and buttons
- Smooth transitions
- Float animation for hero images

### Security

- CSRF protection on all forms
- Password visibility toggle
- Remember me functionality
- Staff-only dashboard access

### Accessibility

- Semantic HTML5 elements
- ARIA labels where needed
- Keyboard navigation support
- High contrast ratios

## Usage

### Running the Application

1. **Start Django Server**:

```bash
python manage.py runserver
```

2. **Start Fuseki Server** (required for AI features):

```bash
cd C:\apache-jena-fuseki-5.6.0
.\fuseki-server.bat
```

3. **Access the Application**:

- Home: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Signup: http://127.0.0.1:8000/signup/
- Dashboard: http://127.0.0.1:8000/dashboard/ (admin only)
- AI Test: http://127.0.0.1:8000/api/ai/test/

### Creating Admin User

```bash
python manage.py createsuperuser
```

Follow prompts to create admin account, then login to access dashboard.

## Customization

### Changing Colors

Edit CSS variables in template `<style>` sections:

```css
:root {
  --primary-blue: #your-color;
  --secondary-blue: #your-color;
  /* ... */
}
```

### Adding New Pages

1. Create template in `templates/` directory
2. Extend `base.html`
3. Create view in `apps/users/views.py`
4. Add URL route in `Smart_Health/urls.py`

### Modifying Dashboard Stats

Update `dashboard_view()` in `apps/users/views.py`:

```python
context = {
    'total_users': User.objects.count(),
    'total_activities': Activity.objects.count(),
    # Add your stats here
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Dependencies

- Django 4.2.7
- Bootstrap 5.3.0
- Bootstrap Icons 1.11.0
- Google Fonts (Poppins)

## Notes

- All forms include CSRF protection
- Templates use Django template language
- Static files served in development mode
- Production deployment requires additional configuration

## Future Enhancements

- [ ] User profile pages
- [ ] Activity tracking interface
- [ ] Meal planning UI
- [ ] Health metrics visualization
- [ ] Mobile app version
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Social authentication integration

## License

This project is part of Smart Health Web application.
