import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Package, FolderTree, ShoppingCart, Users, Star, Tag, Image, Settings } from 'lucide-react';

const AdminLayout = ({ children }) => {
  const location = useLocation();

  const menuItems = [
    { path: '/admin', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/admin/products', icon: Package, label: 'Products' },
    { path: '/admin/categories', icon: FolderTree, label: 'Categories' },
    { path: '/admin/orders', icon: ShoppingCart, label: 'Orders' },
    { path: '/admin/customers', icon: Users, label: 'Customers' },
    { path: '/admin/reviews', icon: Star, label: 'Reviews' },
    { path: '/admin/coupons', icon: Tag, label: 'Coupons' },
    { path: '/admin/banners', icon: Image, label: 'Banners' },
    { path: '/admin/settings', icon: Settings, label: 'Settings' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950" data-testid="admin-layout">
      <div className="flex">
        <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 min-h-screen fixed">
          <div className="p-6 border-b border-gray-200 dark:border-gray-800">
            <Link to="/admin" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xl">E</span>
              </div>
              <span className="text-xl font-black text-gray-900 dark:text-white">Admin</span>
            </Link>
          </div>
          <nav className="p-4 space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                  data-testid={`admin-nav-${item.label.toLowerCase()}`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </aside>

        <main className="flex-1 ml-64">
          <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
            <div className="px-8 py-4 flex items-center justify-between">
              <h1 className="text-2xl font-black text-gray-900 dark:text-white">Admin Panel</h1>
              <Link to="/" className="text-sm text-orange-500 hover:underline" data-testid="back-to-store">
                Back to Store
              </Link>
            </div>
          </header>
          <div className="p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;