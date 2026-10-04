import { TextLink } from '../components/common/TextLink'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center gap-2 py-20 text-center">
      <h1 className="text-lg font-semibold text-slate-900">Page not found</h1>
      <p className="text-sm text-slate-500">
        The page you are looking for does not exist. <TextLink to="/dashboard">Go to the dashboard</TextLink>
      </p>
    </div>
  )
}
