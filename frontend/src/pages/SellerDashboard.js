import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Package, DollarSign, ShoppingCart, Plus, Edit, Trash2, LogOut } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SellerDashboard = () => {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({ totalProducts: 0, totalRevenue: 0, totalOrders: 0 });
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    price: 0,
    discount_price: null,
    images: [],
    category_id: '',
    stock: 0,
    active: true,
    specifications: {}
  });

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }
    if (user.role !== 'seller' && user.role !== 'admin') {
      navigate('/');
      toast.error('Seller access required');
      return;
    }
    fetchData();
  }, [user]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [productsRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/products?active_only=false`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/categories`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      setProducts(productsRes.data);
      setCategories(categoriesRes.data);
      
      const totalProducts = productsRes.data.length;
      const totalRevenue = productsRes.data.reduce((sum, p) => sum + (p.price * p.stock), 0);
      setStats({ totalProducts, totalRevenue, totalOrders: 0 });
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingProduct) {
        await axios.put(`${API}/products/${editingProduct.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Product updated successfully');
      } else {
        await axios.post(`${API}/products`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Product added successfully');
      }
      fetchData();
      setModalOpen(false);
      resetForm();
    } catch (error) {
      toast.error('Failed to save product');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this product?')) return;
    try {
      await axios.delete(`${API}/products/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Product deleted');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete product');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      slug: '',
      description: '',
      price: 0,
      discount_price: null,
      images: [],
      category_id: '',
      stock: 0,
      active: true,
      specifications: {}
    });
    setEditingProduct(null);
  };

  const openEditModal = (product) => {
    setEditingProduct(product);
    setFormData(product);
    setModalOpen(true);
  };

  if (!user || (user.role !== 'seller' && user.role !== 'admin')) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950" data-testid="seller-dashboard">
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-black text-xl">E</span>
              </div>
              <span className="text-xl font-black text-gray-900 dark:text-white">Seller Panel</span>
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">Welcome, {user.name}</span>
            <Link to="/">
              <Button variant="outline" size="sm">Back to Store</Button>
            </Link>
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="w-4 h-4 mr-2" /> Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Products
              </CardTitle>
              <Package className="w-5 h-5 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black text-gray-900 dark:text-white">
                {stats.totalProducts}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Inventory Value
              </CardTitle>
              <DollarSign className="w-5 h-5 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black text-gray-900 dark:text-white">
                ${stats.totalRevenue.toFixed(2)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Orders
              </CardTitle>
              <ShoppingCart className="w-5 h-5 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black text-gray-900 dark:text-white">
                {stats.totalOrders}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-black text-gray-900 dark:text-white">My Products</h2>
            <Button 
              onClick={() => setModalOpen(true)} 
              className="bg-orange-500 hover:bg-orange-600"
              data-testid="add-product-button"
            >
              <Plus className="mr-2 w-4 h-4" /> Add Product
            </Button>
          </div>

          {loading ? (
            <div className="flex justify-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-16">
              <Package className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-4">No products yet</p>
              <Button onClick={() => setModalOpen(true)} className="bg-orange-500 hover:bg-orange-600">
                Add Your First Product
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-gray-200 dark:border-gray-800">
                  <tr>
                    <th className="text-left p-4">Product</th>
                    <th className="text-left p-4">Category</th>
                    <th className="text-left p-4">Price</th>
                    <th className="text-left p-4">Stock</th>
                    <th className="text-left p-4">Status</th>
                    <th className="text-right p-4">Actions</th>
                  </tr>
                </thead>
                <tbody data-testid="products-table">
                  {products.map((product) => (
                    <tr key={product.id} className="border-b border-gray-200 dark:border-gray-800 last:border-0">
                      <td className="p-4">
                        <div className="flex items-center space-x-3">
                          <img
                            src={product.images[0] || 'https://via.placeholder.com/50'}
                            alt={product.name}
                            className="w-12 h-12 object-cover rounded"
                          />
                          <span className="font-medium">{product.name}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        {categories.find(c => c.id === product.category_id)?.name || '-'}
                      </td>
                      <td className="p-4 font-bold">${product.price}</td>
                      <td className="p-4">{product.stock}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded text-xs ${
                          product.active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {product.active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="p-4 text-right space-x-2">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => openEditModal(product)}
                          data-testid={`edit-product-${product.id}`}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleDelete(product.id)}
                          data-testid={`delete-product-${product.id}`}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="product-modal">
          <DialogHeader>
            <DialogTitle>{editingProduct ? 'Edit Product' : 'Add New Product'}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Product Name</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                data-testid="product-name-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Slug (URL-friendly name)</label>
              <Input
                value={formData.slug}
                onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                required
                data-testid="product-slug-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border rounded-lg"
                required
                data-testid="product-description-input"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Price ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                  required
                  data-testid="product-price-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Discount Price ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.discount_price || ''}
                  onChange={(e) => setFormData({ ...formData, discount_price: e.target.value ? parseFloat(e.target.value) : null })}
                  data-testid="product-discount-input"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Category</label>
              <Select 
                value={formData.category_id} 
                onValueChange={(value) => setFormData({ ...formData, category_id: value })}
              >
                <SelectTrigger data-testid="product-category-select">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Stock Quantity</label>
              <Input
                type="number"
                value={formData.stock}
                onChange={(e) => setFormData({ ...formData, stock: parseInt(e.target.value) })}
                required
                data-testid="product-stock-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Image URLs (comma-separated)</label>
              <Input
                value={formData.images.join(',')}
                onChange={(e) => setFormData({ ...formData, images: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                placeholder="https://example.com/image1.jpg, https://example.com/image2.jpg"
                data-testid="product-images-input"
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.active}
                onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                data-testid="product-active-checkbox"
              />
              <label className="text-sm font-medium">Product Active (visible to customers)</label>
            </div>
            <Button 
              type="submit" 
              className="w-full bg-orange-500 hover:bg-orange-600"
              data-testid="save-product-button"
            >
              {editingProduct ? 'Update Product' : 'Add Product'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SellerDashboard;
