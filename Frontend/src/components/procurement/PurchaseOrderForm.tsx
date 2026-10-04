import { useState, type FormEvent } from 'react'

import { useToast } from '../../context/ToastContext'
import { useApi } from '../../hooks/useApi'
import { getErrorMessage } from '../../services/api'
import { procurementService } from '../../services/procurementService'
import { supplierService } from '../../services/supplierService'
import type { PurchaseOrder, PurchaseOrderInput } from '../../types'
import { Button } from '../common/Button'
import { Modal } from '../common/Modal'
import { QueryBoundary } from '../common/QueryBoundary'

interface PurchaseOrderFormProps {
  /** When provided, the form edits this draft instead of creating a new one. */
  purchaseOrder?: PurchaseOrder
  /** Starting values for a new draft, e.g. from a reorder suggestion. The user can change them. */
  defaults?: Partial<Pick<PurchaseOrderInput, 'supplier_id' | 'product_id' | 'quantity' | 'reason'>>
  onClose: () => void
  onSaved: (purchaseOrder: PurchaseOrder) => void
}

const FORM_ID = 'purchase-order-form'

export function PurchaseOrderForm({ purchaseOrder, defaults, onClose, onSaved }: PurchaseOrderFormProps) {
  const toast = useToast()
  const suppliers = useApi(() => supplierService.getSuppliers({ status: 'Active' }), [])
  const [supplierId, setSupplierId] = useState(purchaseOrder?.supplier_id ?? defaults?.supplier_id ?? '')
  const [productId, setProductId] = useState(purchaseOrder?.product_id ?? defaults?.product_id ?? '')
  const [quantity, setQuantity] = useState(String(purchaseOrder?.quantity ?? defaults?.quantity ?? ''))
  const [unitPrice, setUnitPrice] = useState(purchaseOrder ? String(purchaseOrder.unit_price) : '')
  const [expectedDelivery, setExpectedDelivery] = useState(purchaseOrder?.expected_delivery ?? '')
  const [reason, setReason] = useState(purchaseOrder?.reason ?? defaults?.reason ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const input: PurchaseOrderInput = {
      supplier_id: supplierId,
      product_id: productId,
      quantity: Number(quantity),
      reason,
      ...(unitPrice ? { unit_price: Number(unitPrice) } : {}),
      ...(expectedDelivery ? { expected_delivery: expectedDelivery } : {}),
    }
    setSaving(true)
    setError(null)
    try {
      const saved = purchaseOrder
        ? await procurementService.updateDraft(purchaseOrder.id, input)
        : await procurementService.createDraft(input)
      toast.success(purchaseOrder ? `${saved.id} updated.` : `Draft ${saved.id} created.`)
      onSaved(saved)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      title={purchaseOrder ? `Edit ${purchaseOrder.id}` : 'New purchase order draft'}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" form={FORM_ID} variant="primary" disabled={saving || !suppliers.data}>
            {saving ? 'Saving...' : purchaseOrder ? 'Save changes' : 'Create draft'}
          </Button>
        </>
      }
    >
      <QueryBoundary state={suppliers} resource="suppliers">
        {(supplierList) => {
          const products = supplierList.find((s) => s.id === supplierId)?.products_supplied ?? []
          return (
            <form id={FORM_ID} onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
                  {error}
                </p>
              )}
              <div>
                <label htmlFor="po-supplier" className="field-label">
                  Supplier
                </label>
                <select
                  id="po-supplier"
                  className="field"
                  required
                  value={supplierId}
                  onChange={(event) => {
                    setSupplierId(event.target.value)
                    setProductId('')
                  }}
                >
                  <option value="">Select a supplier</option>
                  {supplierList.map((supplier) => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="po-product" className="field-label">
                  Product
                </label>
                <select
                  id="po-product"
                  className="field"
                  required
                  disabled={!supplierId}
                  value={productId}
                  onChange={(event) => setProductId(event.target.value)}
                >
                  <option value="">{supplierId ? 'Select a product' : 'Select a supplier first'}</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name} ({product.sku})
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="po-quantity" className="field-label">
                    Quantity
                  </label>
                  <input
                    id="po-quantity"
                    type="number"
                    min={1}
                    step={1}
                    required
                    className="field"
                    value={quantity}
                    onChange={(event) => setQuantity(event.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor="po-unit-price" className="field-label">
                    Unit price (USD)
                  </label>
                  <input
                    id="po-unit-price"
                    type="number"
                    min={0.01}
                    step={0.01}
                    className="field"
                    placeholder="Standard cost"
                    value={unitPrice}
                    onChange={(event) => setUnitPrice(event.target.value)}
                  />
                </div>
              </div>
              <div>
                <label htmlFor="po-expected" className="field-label">
                  Expected delivery
                </label>
                <input
                  id="po-expected"
                  type="date"
                  className="field"
                  value={expectedDelivery}
                  onChange={(event) => setExpectedDelivery(event.target.value)}
                />
                <p className="mt-1 text-xs text-slate-500">
                  Leave blank to use the supplier's average delivery time.
                </p>
              </div>
              <div>
                <label htmlFor="po-reason" className="field-label">
                  Reason
                </label>
                <textarea
                  id="po-reason"
                  rows={2}
                  maxLength={500}
                  className="field"
                  placeholder="e.g. Replenishment required"
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                />
              </div>
            </form>
          )
        }}
      </QueryBoundary>
    </Modal>
  )
}
