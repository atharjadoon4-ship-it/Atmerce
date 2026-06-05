import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useCart } from '@/contexts/CartContext';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Checkout = () => {
  const { cart, getCartTotal, clearCart } = useCart();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [shippingAddress, setShippingAddress] = useState({
    full_name: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    phone: ''
  });
  const [couponCode, setCouponCode] = useState('');
  const [discount, setDiscount] = useState(0);

  const handleApplyCoupon = async () => {
    try {
      const response = await axios.get(`${API}/coupons/validate/${couponCode}?total=${getCartTotal()}`);
      setDiscount(response.data.discount);
      toast.success(`Coupon applied! Discount: $${response.data.discount}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid coupon');
    }
  };

  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    if (!user) {
      toast.error('Please login to place order');
      return;
    }

    setLoading(true);
    try {
      const orderData = {
        items: cart.map(item => ({
          product_id: item.id,
          name: item.name,
          price: item.discount_price || item.price,
          quantity: item.quantity
        })),
        total: getCartTotal() - discount,
        shipping_address: shippingAddress,
        coupon_code: couponCode || null
      };

      const response = await axios.post(`${API}/orders`, orderData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Order placed successfully!');
      clearCart();
      navigate(`/orders/${response.data.id}`);
    } catch (error) {
      toast.error('Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    navigate('/cart');
    return null;
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950" data-testid="checkout-page">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-4xl font-black tracking-tight text-gray-900 dark:text-white mb-8" data-testid="checkout-title">
          Checkout
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <form onSubmit={handlePlaceOrder} className="space-y-6">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Shipping Address</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Full Name</label>
                    <Input
                      value={shippingAddress.full_name}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, full_name: e.target.value })}
                      required
                      data-testid="shipping-name-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Phone</label>
                    <Input
                      value={shippingAddress.phone}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, phone: e.target.value })}
                      required
                      data-testid="shipping-phone-input"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium mb-2">Address</label>
                    <Input
                      value={shippingAddress.address}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, address: e.target.value })}
                      required
                      data-testid="shipping-address-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">City</label>
                    <Input
                      value={shippingAddress.city}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, city: e.target.value })}
                      required
                      data-testid="shipping-city-input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">State</label>
                    <Input
                      value={shippingAddress.state}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, state: e.target.value })}
                      required
                      data-testid="shipping-state-input"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium mb-2">ZIP Code</label>
                    <Input
                      value={shippingAddress.zip_code}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, zip_code: e.target.value })}
                      required
                      data-testid="shipping-zip-input"
                    />
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-orange-500 hover:bg-orange-600 py-6"
                data-testid="place-order-button"
              >
                {loading ? 'Placing Order...' : 'Place Order'}
              </Button>
            </form>
          </div>

          <div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 sticky top-24">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Order Summary</h2>
              
              <div className="space-y-4 mb-6">
                {cart.map((item) => {
                  const price = item.discount_price || item.price;
                  return (
                    <div key={item.id} className="flex items-center space-x-3">
                      <img
                        src={item.images[0] || 'https://images.unsplash.com/photo-1515940175183-6798529cb860?crop=entropy&cs=srgb&fm=jpg&q=85'}
                        alt={item.name}
                        className="w-16 h-16 object-cover rounded"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white line-clamp-1">{item.name}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Qty: {item.quantity}</p>
                      </div>
                      <p className="font-medium text-gray-900 dark:text-white">${(price * item.quantity).toFixed(2)}</p>
                    </div>
                  );
                })}
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Coupon Code</label>
                <div className="flex space-x-2">
                  <Input
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    placeholder="Enter coupon code"
                    data-testid="coupon-input"
                  />
                  <Button
                    type="button"
                    onClick={handleApplyCoupon}
                    variant="outline"
                    data-testid="apply-coupon-button"
                  >
                    Apply
                  </Button>
                </div>
              </div>

              <div className="space-y-2 border-t border-gray-200 dark:border-gray-800 pt-4">
                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                  <span>Subtotal</span>
                  <span>${getCartTotal().toFixed(2)}</span>
                </div>
                {discount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Discount</span>
                    <span>-${discount.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                  <span>Shipping</span>
                  <span>Free</span>
                </div>
                <div className="border-t border-gray-200 dark:border-gray-800 pt-2 mt-2">
                  <div className="flex justify-between text-lg font-bold text-gray-900 dark:text-white">
                    <span>Total</span>
                    <span data-testid="checkout-total">${(getCartTotal() - discount).toFixed(2)}</span>
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

export default Checkout;