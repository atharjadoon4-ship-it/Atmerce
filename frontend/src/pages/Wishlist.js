import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { useCart } from '@/contexts/CartContext';
import { Heart, Trash2, ShoppingCart } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Wishlist = () => {
  const { user, token } = useAuth();
  const { addToCart } = useCart();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }
    fetchWishlist();
  }, [user]);

  const fetchWishlist = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/wishlist`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch wishlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (productId) => {
    try {
      await axios.delete(`${API}/wishlist/${productId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProducts(products.filter(p => p.id !== productId));
      toast.success('Removed from wishlist');
    } catch (error) {
      toast.error('Failed to remove from wishlist');
    }
  };

  const handleAddToCart = (product) => {
    if (product.stock <= 0) {
      toast.error('Product is out of stock');
      return;
    }
    addToCart(product, 1);
    toast.success('Added to cart!');
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950" data-testid="wishlist-page">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-4xl font-black tracking-tight text-gray-900 dark:text-white mb-8" data-testid="wishlist-title">
          My Wishlist
        </h1>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-16" data-testid="empty-wishlist">
            <Heart className="w-24 h-24 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-4">Your wishlist is empty</p>
            <Link to="/products">
              <Button className="bg-orange-500 hover:bg-orange-600">Explore Products</Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6" data-testid="wishlist-grid">
            {products.map((product) => (
              <div
                key={product.id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                data-testid={`wishlist-item-${product.id}`}
              >
                <Link to={`/products/${product.slug}`}>
                  <div className="aspect-square overflow-hidden">
                    <img
                      src={product.images[0] || 'https://images.unsplash.com/photo-1515940175183-6798529cb860?crop=entropy&cs=srgb&fm=jpg&q=85'}
                      alt={product.name}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                </Link>
                <div className="p-4">
                  <Link to={`/products/${product.slug}`}>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 hover:text-orange-500">
                      {product.name}
                    </h3>
                  </Link>
                  <div className="mb-4">
                    {product.discount_price ? (
                      <div className="flex items-center space-x-2">
                        <span className="text-lg font-bold text-orange-500">${product.discount_price}</span>
                        <span className="text-sm text-gray-500 line-through">${product.price}</span>
                      </div>
                    ) : (
                      <span className="text-lg font-bold text-gray-900 dark:text-white">${product.price}</span>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      onClick={() => handleAddToCart(product)}
                      disabled={product.stock <= 0}
                      className="flex-1 bg-orange-500 hover:bg-orange-600"
                      data-testid={`add-to-cart-${product.id}`}
                    >
                      <ShoppingCart className="w-4 h-4 mr-1" /> Add to Cart
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleRemove(product.id)}
                      data-testid={`remove-${product.id}`}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default Wishlist;