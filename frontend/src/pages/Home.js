import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { ShoppingBag, Star, TrendingUp, Shield, Truck } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Home = () => {
  const [categories, setCategories] = useState([]);
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [banners, setBanners] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [categoriesRes, productsRes, bannersRes] = await Promise.all([
        axios.get(`${API}/categories?active_only=true`),
        axios.get(`${API}/products?active_only=true`),
        axios.get(`${API}/banners?active_only=true`)
      ]);
      setCategories(categoriesRes.data.slice(0, 6));
      setFeaturedProducts(productsRes.data.slice(0, 8));
      setBanners(bannersRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950" data-testid="home-page">
      <Navbar />

      <section className="relative h-[70vh] overflow-hidden bg-gradient-to-br from-orange-50 to-orange-100 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center">
          <div className="max-w-2xl">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-gray-900 dark:text-white mb-6" data-testid="hero-title">
              Discover Your Next
              <span className="block text-orange-500">Favorite Product</span>
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
              Shop from thousands of products with unbeatable prices and fast delivery
            </p>
            <Link to="/products">
              <Button className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-6 text-lg" data-testid="shop-now-button">
                <ShoppingBag className="mr-2" /> Shop Now
              </Button>
            </Link>
          </div>
        </div>
        <div className="absolute right-0 top-0 h-full w-1/2 hidden lg:block">
          <img
            src="https://images.unsplash.com/photo-1515940175183-6798529cb860?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MDV8MHwxfHNlYXJjaHw0fHxtb2Rlcm4lMjB0ZWNoJTIwZ2FkZ2V0c3xlbnwwfHx8fDE3ODA2NjYzMzN8MA&ixlib=rb-4.1.0&q=85"
            alt="Hero"
            className="w-full h-full object-cover"
          />
        </div>
      </section>

      <section className="py-16 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex items-center space-x-4" data-testid="feature-delivery">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-full flex items-center justify-center">
                <Truck className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Free Delivery</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">On orders over $50</p>
              </div>
            </div>
            <div className="flex items-center space-x-4" data-testid="feature-quality">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-full flex items-center justify-center">
                <Shield className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Quality Guaranteed</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">100% authentic products</p>
              </div>
            </div>
            <div className="flex items-center space-x-4" data-testid="feature-support">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-full flex items-center justify-center">
                <Star className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">24/7 Support</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">We're here to help</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-gray-900 dark:text-white" data-testid="categories-title">
              Shop by Category
            </h2>
            <Link to="/products">
              <Button variant="ghost" className="text-orange-500">View All</Button>
            </Link>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4" data-testid="categories-grid">
            {categories.map((category) => (
              <Link
                key={category.id}
                to={`/products?category=${category.slug}`}
                className="group"
                data-testid={`category-card-${category.slug}`}
              >
                <div className="aspect-square rounded-lg overflow-hidden border border-gray-200 dark:border-gray-800 hover:-translate-y-1 transition-transform duration-200">
                  <img
                    src={category.image || 'https://images.unsplash.com/photo-1504610926078-a1611febcad3?crop=entropy&cs=srgb&fm=jpg&q=85'}
                    alt={category.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                </div>
                <h3 className="mt-2 font-medium text-gray-900 dark:text-white text-center">{category.name}</h3>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-gray-900 dark:text-white" data-testid="featured-title">
                Featured Products
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mt-2">Hand-picked items just for you</p>
            </div>
            <Link to="/products">
              <Button variant="ghost" className="text-orange-500">View All</Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6" data-testid="products-grid">
            {featuredProducts.map((product) => (
              <Link
                key={product.id}
                to={`/products/${product.slug}`}
                className="group"
                data-testid={`product-card-${product.slug}`}
              >
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:-translate-y-1 hover:shadow-lg transition-all duration-200">
                  <div className="aspect-square overflow-hidden">
                    <img
                      src={product.images[0] || 'https://images.unsplash.com/photo-1515940175183-6798529cb860?crop=entropy&cs=srgb&fm=jpg&q=85'}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">{product.name}</h3>
                    <div className="flex items-center justify-between">
                      <div>
                        {product.discount_price ? (
                          <div className="flex items-center space-x-2">
                            <span className="text-lg font-bold text-orange-500">${product.discount_price}</span>
                            <span className="text-sm text-gray-500 line-through">${product.price}</span>
                          </div>
                        ) : (
                          <span className="text-lg font-bold text-gray-900 dark:text-white">${product.price}</span>
                        )}
                      </div>
                      {product.ratings_count > 0 && (
                        <div className="flex items-center space-x-1">
                          <Star className="w-4 h-4 fill-orange-500 text-orange-500" />
                          <span className="text-sm text-gray-600 dark:text-gray-400">{product.ratings_avg}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Home;