import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { useCart } from '@/contexts/CartContext';
import { useAuth } from '@/contexts/AuthContext';
import { ShoppingCart, Heart, Star, Minus, Plus } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ProductDetail = () => {
  const { slug } = useParams();
  const { addToCart } = useCart();
  const { user, token } = useAuth();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });
  const [selectedImage, setSelectedImage] = useState(0);

  useEffect(() => {
    fetchProduct();
  }, [slug]);

  const fetchProduct = async () => {
    setLoading(true);
    try {
      const productsRes = await axios.get(`${API}/products?active_only=true`);
      const foundProduct = productsRes.data.find(p => p.slug === slug);
      if (foundProduct) {
        setProduct(foundProduct);
        const reviewsRes = await axios.get(`${API}/reviews?product_id=${foundProduct.id}&approved_only=true`);
        setReviews(reviewsRes.data);
      }
    } catch (error) {
      console.error('Failed to fetch product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (product.stock <= 0) {
      toast.error('Product is out of stock');
      return;
    }
    addToCart(product, quantity);
    toast.success('Added to cart!');
  };

  const handleAddToWishlist = async () => {
    if (!user) {
      toast.error('Please login to add to wishlist');
      return;
    }
    try {
      await axios.post(`${API}/wishlist/${product.id}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Added to wishlist!');
    } catch (error) {
      toast.error('Failed to add to wishlist');
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!user) {
      toast.error('Please login to submit a review');
      return;
    }
    try {
      await axios.post(`${API}/reviews`, {
        product_id: product.id,
        ...reviewForm
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Review submitted for approval!');
      setReviewForm({ rating: 5, comment: '' });
    } catch (error) {
      toast.error('Failed to submit review');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950">
        <Navbar />
        <div className="flex justify-center items-center h-screen" data-testid="loading-spinner">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950">
        <Navbar />
        <div className="flex justify-center items-center h-screen">
          <p className="text-gray-600 dark:text-gray-400">Product not found</p>
        </div>
      </div>
    );
  }

  const price = product.discount_price || product.price;

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950" data-testid="product-detail-page">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div>
            <div className="aspect-square bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden mb-4">
              <img
                src={product.images[selectedImage] || 'https://images.unsplash.com/photo-1515940175183-6798529cb860?crop=entropy&cs=srgb&fm=jpg&q=85'}
                alt={product.name}
                className="w-full h-full object-cover"
                data-testid="product-main-image"
              />
            </div>
            {product.images.length > 1 && (
              <div className="grid grid-cols-4 gap-2">
                {product.images.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedImage(idx)}
                    className={`aspect-square rounded-lg overflow-hidden border-2 ${
                      selectedImage === idx ? 'border-orange-500' : 'border-gray-200 dark:border-gray-700'
                    }`}
                    data-testid={`product-thumbnail-${idx}`}
                  >
                    <img src={img} alt="" className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          <div>
            <h1 className="text-4xl font-black tracking-tight text-gray-900 dark:text-white mb-4" data-testid="product-title">
              {product.name}
            </h1>

            <div className="flex items-center space-x-4 mb-6">
              {product.ratings_count > 0 && (
                <div className="flex items-center space-x-2">
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-5 h-5 ${
                          i < Math.round(product.ratings_avg)
                            ? 'fill-orange-500 text-orange-500'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-gray-600 dark:text-gray-400">({product.ratings_count} reviews)</span>
                </div>
              )}
              {product.stock > 0 ? (
                <span className="text-green-600 font-medium">In Stock</span>
              ) : (
                <span className="text-red-600 font-medium">Out of Stock</span>
              )}
            </div>

            <div className="mb-6">
              {product.discount_price ? (
                <div className="flex items-center space-x-4">
                  <span className="text-4xl font-black text-orange-500" data-testid="product-price">${product.discount_price}</span>
                  <span className="text-2xl text-gray-500 line-through">${product.price}</span>
                  <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm font-medium">
                    {Math.round(((product.price - product.discount_price) / product.price) * 100)}% OFF
                  </span>
                </div>
              ) : (
                <span className="text-4xl font-black text-gray-900 dark:text-white" data-testid="product-price">${product.price}</span>
              )}
            </div>

            <p className="text-gray-600 dark:text-gray-400 mb-8 leading-relaxed" data-testid="product-description">
              {product.description}
            </p>

            <div className="flex items-center space-x-4 mb-8">
              <div className="flex items-center border border-gray-300 dark:border-gray-700 rounded-lg">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  data-testid="quantity-decrease"
                >
                  <Minus className="w-4 h-4" />
                </Button>
                <span className="px-6 py-2 font-medium" data-testid="quantity-value">{quantity}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                  data-testid="quantity-increase"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>

              <Button
                onClick={handleAddToCart}
                disabled={product.stock <= 0}
                className="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-6"
                data-testid="add-to-cart-button"
              >
                <ShoppingCart className="mr-2" /> Add to Cart
              </Button>

              <Button
                variant="outline"
                size="icon"
                className="py-6"
                onClick={handleAddToWishlist}
                data-testid="add-to-wishlist-button"
              >
                <Heart className="w-5 h-5" />
              </Button>
            </div>

            {Object.keys(product.specifications || {}).length > 0 && (
              <div className="border-t border-gray-200 dark:border-gray-800 pt-8">
                <h3 className="text-xl font-bold mb-4">Specifications</h3>
                <dl className="space-y-2">
                  {Object.entries(product.specifications).map(([key, value]) => (
                    <div key={key} className="flex">
                      <dt className="font-medium text-gray-900 dark:text-white w-1/3">{key}:</dt>
                      <dd className="text-gray-600 dark:text-gray-400 w-2/3">{value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}
          </div>
        </div>

        <div className="mt-16">
          <h2 className="text-3xl font-black tracking-tight text-gray-900 dark:text-white mb-8">Customer Reviews</h2>

          {user && (
            <form onSubmit={handleSubmitReview} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 mb-8" data-testid="review-form">
              <h3 className="font-semibold mb-4">Write a Review</h3>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Rating</label>
                <div className="flex space-x-2">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      type="button"
                      onClick={() => setReviewForm({ ...reviewForm, rating })}
                      data-testid={`rating-${rating}`}
                    >
                      <Star
                        className={`w-6 h-6 ${
                          rating <= reviewForm.rating
                            ? 'fill-orange-500 text-orange-500'
                            : 'text-gray-300'
                        }`}
                      />
                    </button>
                  ))}
                </div>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Comment</label>
                <textarea
                  value={reviewForm.comment}
                  onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
                  required
                  data-testid="review-comment-input"
                />
              </div>
              <Button type="submit" className="bg-orange-500 hover:bg-orange-600" data-testid="submit-review-button">
                Submit Review
              </Button>
            </form>
          )}

          <div className="space-y-6" data-testid="reviews-list">
            {reviews.length === 0 ? (
              <p className="text-gray-600 dark:text-gray-400">No reviews yet. Be the first to review this product!</p>
            ) : (
              reviews.map((review) => (
                <div key={review.id} className="border-b border-gray-200 dark:border-gray-800 pb-6" data-testid={`review-${review.id}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">{review.user_name}</p>
                      <div className="flex items-center space-x-2">
                        <div className="flex">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-4 h-4 ${
                                i < review.rating ? 'fill-orange-500 text-orange-500' : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-sm text-gray-500">
                          {new Date(review.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">{review.comment}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default ProductDetail;