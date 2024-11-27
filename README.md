# Nest : E-Commerce Platform

**Nest E-Commerce** is a full-featured eCommerce platform developed using Django. It offers a seamless shopping experience with features like product browsing, shopping cart, wishlist, multiple payment options, and a dynamic offer management system.

## Features

- **User Features**:
  - Secure user authentication (Login, Signup with OTP, Referral Code integration).
  - Wallet system for payments and referral rewards.
  - Downloadable invoices in PDF format for all orders.
  
- **Shopping Experience**:
  - Dynamic product listing with category-level and product-specific offers.
  - AJAX-enabled "Add to Cart" and "Add to Wishlist" functionality.
  - Address management with types: Home, Office, and Other.

- **Admin Features**:
  - Manage products, categories, and offers.
  - Assign offers to categories or individual products.
  - Monitor referral code usage and track wallet credits.

- **Payment System**:
  - Supports Razorpay and Wallet Payments.
  - Retry mechanism for failed payments.
  - Order cancellation and refund processing.

- **Offer Module**:
  - **Category Offers**: Discount on all products within a category.
  - **Product Offers**: Individual product discounts.
  - **Referral Offers**: Wallet credits for referrer and referred users.

## Technology Stack

- **Backend**: Django, Python
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 4
- **Database**: PostgreSQL
- **Payment Gateway**: Razorpay
- **Hosting**: AWS EC2 (Nginx and Gunicorn)
- **Domain**: [nikhilrajpk.in](https://nikhilrajpk.in)

## Installation Instructions

1. Clone the repository:
   ```bash
   git clone [https://github.com/nikhilrajpk/Nest_eCommerce.git](https://github.com/nikhilrajpk/Nest_eCommerce.git)
   cd Nest_eCommerce
