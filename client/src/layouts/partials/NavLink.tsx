import { Link } from '@mui/material'
import React, { FC } from 'react'

interface Props {
	to: string
	text: string
}
const NavLink: FC<Props> = ({ to, text }) => {
	return (
		<>
			<Link href={to} sx={{ textDecoration: 'none' }}>
				{text}
			</Link>
		</>
	)
}
interface Props {
	to: string
}
export default NavLink
