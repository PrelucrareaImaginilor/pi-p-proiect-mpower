import { Box, Stack, Typography } from '@mui/material'
import React, { FC } from 'react'
import Navbar from './partials/Navbar'
import { Outlet } from 'react-router-dom'
import Background from './../assets/nice-grid-pattern.png'

interface Props {
	children: React.ReactNode
}

const MainLayout: FC<Props> = ({ children }) => {
	return (
		<>
			<Box
				sx={{
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					// border: '1px solid red',
					minHeight: '100svh',
					width: '100svw',
					background: `url(${Background}), #110F32`,
					justifyContent: 'center',
					backgroundPosition: 'center',
					backgroundSize: 'cover'
				}}
			>
				<Stack
					sx={{
						flexDirection: 'column',
						justifyContent: 'center',
						flexWrap: 'nowrap',
						wordBreak: 'none',
						textAlign: 'center',
						position: 'fixed',
						top: '0'
					}}
				>
					<Typography
						sx={{
							fontSize: '2.5rem',
							color: '#FFF'
							// wordBreak: 'break-word',
						}}
					>
						Police Radar
					</Typography>
					<Typography
					sx={{
						fontSize: '1rem',
						color: '#4B3FD7',
						background: '#FFF',
						borderRadius: '6px'
					}}
				>
					Powered by OpenCV
				</Typography>
				</Stack>
					
				<Navbar />
				<Stack
					sx={{
						background: 'red',
						height: '100%',
						width: '100%'
					}}
				>
					{children}
				</Stack>
				<Outlet />
			</Box>
		</>
	)
}

export default MainLayout
