import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { User, Package, Heart, LogOut } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Profile = () => {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }
    fetchOrders();
  }, [user]);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrders(response.data.slice(0, 5));
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950" data-testid="profile-page">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-4xl font-black tracking-tight text-gray-900 dark:text-white mb-8" data-testid="profile-title">
          My Account
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-1">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-16 h-16 bg-orange-100 dark:bg-orange-900/20 rounded-full flex items-center justify-center">
                  <User className="w-8 h-8 text-orange-500" />
                </div>
                <div>
                  <h2 className="font-bold text-gray-900 dark:text-white" data-testid="user-name">{user.name}</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400" data-testid="user-email">{user.email}</p>
                </div>
              </div>

              <nav className="space-y-2">
                <Link to="/orders" data-testid="nav-orders">
                  <Button variant="ghost" className="w-full justify-start">
                    <Package className="mr-2 w-5 h-5" /> My Orders
                  </Button>
                </Link>
                <Link to="/wishlist" data-testid="nav-wishlist">
                  <Button variant="ghost" className="w-full justify-start">
                    <Heart className="mr-2 w-5 h-5" /> Wishlist
                  </Button>
                </Link>
                <Button
                  variant="ghost"
                  className="w-full justify-start text-red-600"
                  onClick={() => {
                    logout();
                    navigate('/');
                  }}
                  data-testid="logout-button"
                >
                  <LogOut className="mr-2 w-5 h-5" /> Logout
                </Button>
              </nav>
            </div>
          </div>

          <div className="md:col-span-2">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recent Orders</h2>
                <Link to="/orders">
                  <Button variant="ghost" className="text-orange-500" data-testid="view-all-orders">
                    View All
                  </Button>
                </Link>
              </div>

              {orders.length === 0 ? (
                <p className="text-gray-600 dark:text-gray-400" data-testid="no-orders">No orders yet</p>
              ) : (
                <div className="space-y-4" data-testid="orders-list">
                  {orders.map((order) => (
                    <Link
                      key={order.id}
                      to={`/orders/${order.id}`}
                      className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-orange-500 transition-colors"
                      data-testid={`order-${order.id}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-gray-900 dark:text-white">Order #{order.id.slice(0, 8)}</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                          order.status === 'shipped' ? 'bg-blue-100 text-blue-800' :
                          order.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">
                          {new Date(order.created_at).toLocaleDateString()}
                        </span>
                        <span className="font-bold text-gray-900 dark:text-white">${order.total.toFixed(2)}</span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Profile;