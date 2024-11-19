import { Box } from '@mui/material'
import React from 'react'
import NavLink from './NavLink'
import { useLocation } from 'react-router-dom'

const Navbar = () => {
	const location = useLocation()
	const [isHome, setIsHome] = React.useState(location.pathname === '/')

	React.useEffect(() => {
		setIsHome(location.pathname === '/')
	}, [location.pathname])

	return (
		<>
			<Box
				sx={{
					display: 'flex',
					flexDirection: isHome ? 'column' : 'row',
					alignItems: isHome ? 'center' : 'flex-start',
					justifyContent: 'center',
					gap: 2,
				}}
			>
				<NavLink to={'/legend'} text={'Legend'} />
				<NavLink to={'/docs'} text={'Documentacion'} />
				<NavLink to={'/video'} text={'Experiment'} />
				<NavLink to={'/'} text={'Home'} />
				{isHome && (
					<Box
						sx={{
							position: 'relative',
						}}
					>
						{/* <img
							src='https://media1.tenor.com/m/wNnalIwS0ygAAAAd/polis-police.gif'
							alt='Police GIF'
							style={{ width: '200px', height: 'auto' }}
						/> */}
					</Box>
				)}
			</Box>
		</>
	)
}

export default Navbar
