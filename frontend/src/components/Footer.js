import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Footer = () => {
  const [settings, setSettings] = useState(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings`);
      setSettings(response.data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  };

  return (
    <footer className="bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-16" data-testid="footer">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xl">E</span>
              </div>
              <span className="text-2xl font-black tracking-tight text-gray-900 dark:text-white">Shop</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Your trusted online shopping destination
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-4 text-gray-900 dark:text-white">Shop</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li><Link to="/products" className="hover:text-orange-500">All Products</Link></li>
              <li><Link to="/products?category=electronics" className="hover:text-orange-500">Electronics</Link></li>
              <li><Link to="/products?category=fashion" className="hover:text-orange-500">Fashion</Link></li>
              <li><Link to="/products?category=home" className="hover:text-orange-500">Home & Living</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4 text-gray-900 dark:text-white">Account</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li><Link to="/profile" className="hover:text-orange-500">My Profile</Link></li>
              <li><Link to="/orders" className="hover:text-orange-500">My Orders</Link></li>
              <li><Link to="/wishlist" className="hover:text-orange-500">Wishlist</Link></li>
              <li><Link to="/cart" className="hover:text-orange-500">Shopping Cart</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4 text-gray-900 dark:text-white">Contact</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              {settings?.contact_email && (
                <li>Email: {settings.contact_email}</li>
              )}
              {settings?.contact_phone && (
                <li>Phone: {settings.contact_phone}</li>
              )}
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-800 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>{settings?.footer_text || '© 2026 E-Shop. All rights reserved.'}</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;