import React, { useState } from "react";

export default function SellerDashboard() {
  const [name, setName] = useState("");
    const [price, setPrice] = useState("");
      const [products, setProducts] = useState([]);

        const addProduct = () => {
            if (!name || !price) return;

                setProducts([
                      ...products,
                            { id: Date.now(), name, price }
                                ]);

                                    setName("");
                                        setPrice("");
                                          };

                                            return (
                                                <div style={{ padding: 20 }}>
                                                      <h1>🏪 Seller Dashboard</h1>

                                                            <input
                                                                    placeholder="Product Name"
                                                                            value={name}
                                                                                    onChange={(e) => setName(e.target.value)}
                                                                                          />

                                                                                                <input
                                                                                                        placeholder="Price"
                                                                                                                value={price}
                                                                                                                        onChange={(e) => setPrice(e.target.value)}
                                                                                                                                style={{ marginLeft: 10 }}
                                                                                                                                      />

                                                                                                                                            <button onClick={addProduct} style={{ marginLeft: 10 }}>
                                                                                                                                                    Add Product
                                                                                                                                                          </button>

                                                                                                                                                                <h3 style={{ marginTop: 20 }}>Products</h3>

                                                                                                                                                                      {products.length === 0 ? (
                                                                                                                                                                              <p>No products yet</p>
                                                                                                                                                                                    ) : (
                                                                                                                                                                                            products.map((p) => (
                                                                                                                                                                                                      <div key={p.id} style={{ marginTop: 10 }}>
                                                                                                                                                                                                                  {p.name} - Rs {p.price}
                                                                                                                                                                                                                            </div>
                                                                                                                                                                                                                                    ))
                                                                                                                                                                                                                                          )}
                                                                                                                                                                                                                                              </div>
                                                                                                                                                                                                                                                );
                                                                                                                                                                                                                                                }.