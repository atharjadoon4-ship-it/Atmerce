import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { useCart } from '@/contexts/CartContext';
import { Minus, Plus, Trash2, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';

const Cart = () => {
  const { cart, updateQuantity, removeFromCart, getCartTotal, clearCart } = useCart();
  const navigate = useNavigate();

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950" data-testid="cart-page">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center" data-testid="empty-cart">
            <ShoppingBag className="w-24 h-24 mx-auto text-gray-300 mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Your cart is empty</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-8">Add some products to get started</p>
            <Link to="/products">
              <Button className="bg-orange-500 hover:bg-orange-600">Continue Shopping</Button>
            </Link>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950" data-testid="cart-page">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-4xl font-black tracking-tight text-gray-900 dark:text-white mb-8" data-testid="cart-title">
          Shopping Cart
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="space-y-4" data-testid="cart-items">
              {cart.map((item) => {
                const price = item.discount_price || item.price;
                return (
                  <div
                    key={item.id}
                    className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 flex items-center space-x-4"
                    data-testid={`cart-item-${item.id}`}
                  >
                    <img
                      src={item.images[0] || 'https://images.unsplash.com/photo-1515940175183-6798529cb860?crop=entropy&cs=srgb&fm=jpg&q=85'}
                      alt={item.name}
                      className="w-24 h-24 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{item.name}</h3>
                      <p className="text-orange-500 font-bold">${price}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        data-testid={`decrease-quantity-${item.id}`}
                      >
                        <Minus className="w-4 h-4" />
                      </Button>
                      <span className="w-12 text-center font-medium" data-testid={`quantity-${item.id}`}>{item.quantity}</span>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        data-testid={`increase-quantity-${item.id}`}
                      >
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-gray-900 dark:text-white">${(price * item.quantity).toFixed(2)}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        removeFromCart(item.id);
                        toast.success('Item removed from cart');
                      }}
                      data-testid={`remove-item-${item.id}`}
                    >
                      <Trash2 className="w-5 h-5 text-red-500" />
                    </Button>
                  </div>
                );
              })}
            </div>

            <Button
              variant="outline"
              onClick={() => {
                clearCart();
                toast.success('Cart cleared');
              }}
              className="mt-4"
              data-testid="clear-cart-button"
            >
              Clear Cart
            </Button>
          </div>

          <div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 sticky top-24" data-testid="cart-summary">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Order Summary</h2>
              <div className="space-y-2 mb-6">
                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                  <span>Subtotal</span>
                  <span data-testid="cart-subtotal">${getCartTotal().toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600 dark:text-gray-400">
                  <span>Shipping</span>
                  <span>Free</span>
                </div>
                <div className="border-t border-gray-200 dark:border-gray-800 pt-2 mt-2">
                  <div className="flex justify-between text-lg font-bold text-gray-900 dark:text-white">
                    <span>Total</span>
                    <span data-testid="cart-total">${getCartTotal().toFixed(2)}</span>
                  </div>
                </div>
              </div>
              <Button
                onClick={() => navigate('/checkout')}
                className="w-full bg-orange-500 hover:bg-orange-600 py-6"
                data-testid="checkout-button"
              >
                Proceed to Checkout
              </Button>
              <Link to="/products">
                <Button variant="outline" className="w-full mt-4" data-testid="continue-shopping-button">
                  Continue Shopping
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Cart;