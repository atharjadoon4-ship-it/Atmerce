import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import AdminLayout from '@/components/AdminLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Package, ShoppingCart, Users, DollarSign } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AdminDashboard = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/admin/login');
      return;
    }
    fetchStats();
  }, [user]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user || user.role !== 'admin') return null;

  return (
    <AdminLayout>
      <div data-testid="admin-dashboard">
        <h2 className="text-3xl font-black tracking-tight text-gray-900 dark:text-white mb-8">
          Dashboard Overview
        </h2>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card data-testid="stat-revenue">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Revenue
                  </CardTitle>
                  <DollarSign className="w-5 h-5 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-black text-gray-900 dark:text-white">
                    ${stats?.total_revenue?.toFixed(2) || '0.00'}
                  </div>
                </CardContent>
              </Card>

              <Card data-testid="stat-orders">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Orders
                  </CardTitle>
                  <ShoppingCart className="w-5 h-5 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-black text-gray-900 dark:text-white">
                    {stats?.total_orders || 0}
                  </div>
                </CardContent>
              </Card>

              <Card data-testid="stat-products">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Products
                  </CardTitle>
                  <Package className="w-5 h-5 text-orange-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-black text-gray-900 dark:text-white">
                    {stats?.total_products || 0}
                  </div>
                </CardContent>
              </Card>

              <Card data-testid="stat-customers">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Customers
                  </CardTitle>
                  <Users className="w-5 h-5 text-purple-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-black text-gray-900 dark:text-white">
                    {stats?.total_customers || 0}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Recent Orders</CardTitle>
              </CardHeader>
              <CardContent>
                {stats?.recent_orders?.length === 0 ? (
                  <p className="text-gray-600 dark:text-gray-400">No orders yet</p>
                ) : (
                  <div className="space-y-4" data-testid="recent-orders-list">
                    {stats?.recent_orders?.map((order) => (
                      <div
                        key={order.id}
                        className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-800 rounded-lg"
                      >
                        <div>
                          <p className="font-semibold text-gray-900 dark:text-white">
                            Order #{order.id.slice(0, 8)}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {new Date(order.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-gray-900 dark:text-white">
                            ${order.total.toFixed(2)}
                          </p>
                          <span
                            className={`text-xs px-2 py-1 rounded ${
                              order.status === 'delivered'
                                ? 'bg-green-100 text-green-800'
                                : order.status === 'shipped'
                                ? 'bg-blue-100 text-blue-800'
                                : order.status === 'processing'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {order.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminDashboard;
