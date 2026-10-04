const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
const currencyExact = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })
const compactCurrency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  notation: 'compact',
  maximumFractionDigits: 1,
})
const number = new Intl.NumberFormat('en-US')
const dateFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
const dateTimeFormat = new Intl.DateTimeFormat('en-GB', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

export const formatCurrency = (value: number): string => currency.format(value)
export const formatPrice = (value: number): string => currencyExact.format(value)
export const formatCompactCurrency = (value: number): string => compactCurrency.format(value)
export const formatNumber = (value: number): string => number.format(value)

/** Formats an ISO date (YYYY-MM-DD) without shifting it across time zones. */
export const formatDate = (iso: string | null | undefined): string =>
  iso ? dateFormat.format(new Date(`${iso.slice(0, 10)}T00:00:00`)) : '—'

export const formatDateTime = (iso: string | null | undefined): string =>
  iso ? dateTimeFormat.format(new Date(iso)) : '—'

export const formatRole = (role: string): string =>
  role
    .toLowerCase()
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

const shortDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short' })

/** "05 Oct" - for chart axes. */
export const formatShortDate = (iso: string): string => shortDate.format(new Date(`${iso.slice(0, 10)}T00:00:00`))
