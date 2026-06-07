import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import { CartProvider } from '@/contexts/CartContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { Toaster } from '@/components/ui/sonner';
import ProtectedRoute from '@/components/ProtectedRoute';
import Home from '@/pages/Home';
import Products from '@/pages/Products';
import ProductDetail from '@/pages/ProductDetail';
import Cart from '@/pages/Cart';
import Checkout from '@/pages/Checkout';
import Profile from '@/pages/Profile';
import Orders from '@/pages/Orders';
import OrderDetail from '@/pages/OrderDetail';
import Wishlist from '@/pages/Wishlist';
import BuyerDashboard from '@/pages/BuyerDashboard';
import AdminLogin from '@/pages/admin/AdminLogin';
import AdminDashboard from '@/pages/admin/AdminDashboard';
import AdminProducts from '@/pages/admin/AdminProducts';
import AdminCategories from '@/pages/admin/AdminCategories';
import AdminOrders from '@/pages/admin/AdminOrders';
import AdminCustomers from '@/pages/admin/AdminCustomers';
import AdminReviews from '@/pages/admin/AdminReviews';
import AdminCoupons from '@/pages/admin/AdminCoupons';
import AdminBanners from '@/pages/admin/AdminBanners';
import AdminSettings from '@/pages/admin/AdminSettings';
import SellerDashboard from '@/pages/SellerDashboard';
import SellerRegister from '@/pages/SellerRegister';
import '@/App.css';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <CartProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/products" element={<Products />} />
              <Route path="/products/:slug" element={<ProductDetail />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/checkout" element={<Checkout />} />
              
              {/* Buyer/Customer Routes */}
              <Route path="/buyer/dashboard" element={
                <ProtectedRoute allowedRoles={['customer']}>
                  <BuyerDashboard />
                </ProtectedRoute>
              } />
              <Route path="/profile" element={
                <ProtectedRoute allowedRoles={['customer']}>
                  <Profile />
                </ProtectedRoute>
              } />
              <Route path="/orders" element={
                <ProtectedRoute allowedRoles={['customer']}>
                  <Orders />
                </ProtectedRoute>
              } />
              <Route path="/orders/:orderId" element={
                <ProtectedRoute allowedRoles={['customer']}>
                  <OrderDetail />
                </ProtectedRoute>
              } />
              <Route path="/wishlist" element={
                <ProtectedRoute allowedRoles={['customer']}>
                  <Wishlist />
                </ProtectedRoute>
              } />
              
              {/* Admin/Seller Routes */}
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              <Route path="/admin/products" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminProducts />
                </ProtectedRoute>
              } />
              <Route path="/admin/categories" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminCategories />
                </ProtectedRoute>
              } />
              <Route path="/admin/orders" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminOrders />
                </ProtectedRoute>
              } />
              <Route path="/admin/customers" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminCustomers />
                </ProtectedRoute>
              } />
              <Route path="/admin/reviews" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminReviews />
                </ProtectedRoute>
              } />
              <Route path="/admin/coupons" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminCoupons />
                </ProtectedRoute>
              } />
              <Route path="/admin/banners" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminBanners />
                </ProtectedRoute>
              } />
              <Route path="/admin/settings" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <AdminSettings />
                </ProtectedRoute>
              } />
              <Route path="/seller" element={
                <ProtectedRoute allowedRoles={['admin', 'seller']}>
                  <SellerDashboard />
                </ProtectedRoute>
              } />
              <Route path="/seller/register" element={<SellerRegister />} />
            </Routes>
            <Toaster />
          </BrowserRouter>
        </CartProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
