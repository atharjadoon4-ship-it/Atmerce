import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { useAuth } from '@/contexts/AuthContext';
import { CheckCircle2, Package, Truck, Home } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const OrderDetail = () => {
  const { orderId } = useParams();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }
    fetchOrder();
  }, [orderId, user]);

  const fetchOrder = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/orders/${orderId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrder(response.data);
    } catch (error) {
      console.error('Failed to fetch order:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user || loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950">
        <Navbar />
        <div className="flex justify-center items-center h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950">
        <Navbar />
        <div className="flex justify-center items-center h-screen">
          <p className="text-gray-600 dark:text-gray-400">Order not found</p>
        </div>
      </div>
    );
  }

  const statusSteps = [
    { key: 'pending', label: 'Order Placed', icon: Package },
    { key: 'processing', label: 'Processing', icon: Package },
    { key: 'shipped', label: 'Shipped', icon: Truck },
    { key: 'delivered', label: 'Delivered', icon: Home }
  ];

  const currentStepIndex = statusSteps.findIndex(s => s.key === order.status);

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950" data-testid="order-detail-page">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-4xl font-black tracking-tight text-gray-900 dark:text-white mb-2" data-testid="order-detail-title">
          Order Details
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8" data-testid="order-id">
          Order #{order.id}
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Order Status</h2>
              <div className="relative">
                <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200 dark:bg-gray-700"></div>
                <div
                  className="absolute top-5 left-0 h-0.5 bg-orange-500 transition-all duration-500"
                  style={{ width: `${(currentStepIndex / (statusSteps.length - 1)) * 100}%` }}
                ></div>
                <div className="relative flex justify-between">
                  {statusSteps.map((step, index) => {
                    const StepIcon = step.icon;
                    const isCompleted = index <= currentStepIndex;
                    return (
                      <div key={step.key} className="flex flex-col items-center">
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            isCompleted
                              ? 'bg-orange-500 text-white'
                              : 'bg-gray-200 dark:bg-gray-700 text-gray-400'
                          }`}
                        >
                          <StepIcon className="w-5 h-5" />
                        </div>
                        <p className="text-xs mt-2 text-center text-gray-600 dark:text-gray-400">
                          {step.label}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Items</h2>
              <div className="space-y-4" data-testid="order-items">
                {order.items.map((item, index) => (
                  <div key={index} className="flex items-center space-x-4 pb-4 border-b border-gray-200 dark:border-gray-700 last:border-0">
                    <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded"></div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{item.name}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Quantity: {item.quantity}</p>
                    </div>
                    <p className="font-bold text-gray-900 dark:text-white">${(item.price * item.quantity).toFixed(2)}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Shipping Address</h2>
              <div className="text-gray-600 dark:text-gray-400" data-testid="shipping-address">
                <p className="font-semibold text-gray-900 dark:text-white">{order.shipping_address.full_name}</p>
                <p>{order.shipping_address.address}</p>
                <p>
                  {order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.zip_code}
                </p>
                <p className="mt-2">Phone: {order.shipping_address.phone}</p>
              </div>
            </div>
          </div>

          <div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 sticky top-24">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Order Summary</h2>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                  <span>Order Date</span>
                  <span>{new Date(order.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                  <span>Status</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                    order.status === 'shipped' ? 'bg-blue-100 text-blue-800' :
                    order.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                  </span>
                </div>
                <div className="border-t border-gray-200 dark:border-gray-800 pt-4 mt-4">
                  <div className="flex justify-between text-lg font-bold text-gray-900 dark:text-white">
                    <span>Total</span>
                    <span data-testid="order-total">${order.total.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default OrderDetail;