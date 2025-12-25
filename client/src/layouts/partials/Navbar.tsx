import { Box, Stack } from '@mui/material'
import React from 'react'
import NavLink from './NavLink'
import { useLocation } from 'react-router-dom'

const Navbar = () => {
	const location = useLocation()

	return (
		<Box
			sx={{
				display: 'flex',
				justifyContent: 'center',
				alignItems: 'center',
				width: '100%'
			}}
		>
			<Stack
				direction="column"
				spacing={2}
				sx={{
					width: '100%',
					alignItems: 'stretch'
				}}
			>
				<NavLink to={'/'} text={'Home'} />
				<NavLink to={'/legend'} text={'Features'} />
				<NavLink to={'/video'} text={'Stabilize Video'} />
				<NavLink to={'/docs'} text={'Documentation'} />
			</Stack>
		</Box>
	)
}

export default Navbar
