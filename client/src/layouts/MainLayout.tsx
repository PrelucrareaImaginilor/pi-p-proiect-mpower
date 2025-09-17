import { Box, Stack, Typography, Container, Drawer, useMediaQuery, useTheme } from '@mui/material'
import React, { FC, useState } from 'react'
import Navbar from './partials/Navbar'
import { Outlet } from 'react-router-dom'
import Background from './../assets/nice-grid-pattern.png'

interface Props {
	children: React.ReactNode
}

const MainLayout: FC<Props> = ({ children }) => {
	const theme = useTheme()
	const isMobile = useMediaQuery(theme.breakpoints.down('md'))
	const [drawerOpen, setDrawerOpen] = useState(false)

	const handleDrawerToggle = () => {
		setDrawerOpen(!drawerOpen)
	}

	const drawerWidth = 250

	return (
		<Box
			sx={{
				minHeight: '100vh',
				width: '100%',
				background: ` #110F32`,
				backgroundPosition: 'center',
				backgroundSize: 'cover',
				display: 'flex'
			}}
		>
			{/* Desktop Sidebar */}
			<Box
				sx={{
					width: { xs: 0, md: drawerWidth },
					flexShrink: 0,
					'& .MuiDrawer-paper': {
						width: drawerWidth,
						boxSizing: 'border-box',
						backgroundColor: 'rgba(17, 15, 50, 0.95)',
						backdropFilter: 'blur(10px)',
						borderRight: '1px solid rgba(75, 63, 215, 0.2)',
					},
					display: { xs: 'none', md: 'block' }
				}}
			>
				<Box sx={{ p: 3 }}>
					<Stack
						sx={{
							flexDirection: 'column',
							alignItems: 'center',
							textAlign: 'center',
							gap: 1,
							mb: 4
						}}
					>
						<Typography
							sx={{
								fontSize: '1.5rem',
								color: '#FFF',
								fontWeight: 700
							}}
						>
							Video Stabilizer
						</Typography>
						<Typography
							sx={{
								fontSize: '0.8rem',
								color: '#4B3FD7',
								background: '#FFF',
								borderRadius: '6px',
								px: 2,
								py: 0.5
							}}
						>
							Powered by OpenCV & AI
						</Typography>
					</Stack>
					
					<Navbar />
				</Box>
			</Box>

			{/* Mobile Drawer */}
			<Drawer
				variant="temporary"
				open={drawerOpen}
				onClose={handleDrawerToggle}
				ModalProps={{
					keepMounted: true, // Better open performance on mobile.
				}}
				sx={{
					display: { xs: 'block', md: 'none' },
					'& .MuiDrawer-paper': {
						boxSizing: 'border-box',
						width: drawerWidth,
						backgroundColor: 'rgba(17, 15, 50, 0.95)',
						backdropFilter: 'blur(10px)',
					},
				}}
			>
				<Box sx={{ p: 3 }}>
					<Stack
						sx={{
							flexDirection: 'column',
							alignItems: 'center',
							textAlign: 'center',
							gap: 1,
							mb: 4
						}}
					>
						<Typography
							sx={{
								fontSize: '1.5rem',
								color: '#FFF',
								fontWeight: 700
							}}
						>
							Video Stabilizer
						</Typography>
						<Typography
							sx={{
								fontSize: '0.8rem',
								color: '#4B3FD7',
								background: '#FFF',
								borderRadius: '6px',
								px: 2,
								py: 0.5
							}}
						>
							Powered by OpenCV & AI
						</Typography>
					</Stack>
					
					<Navbar />
				</Box>
			</Drawer>

			{/* Main Content Area */}
			<Box
				component="main"
				sx={{
					flexGrow: 1,
					width: { xs: '100%', md: `calc(100% - ${drawerWidth}px)` },
					display: 'flex',
					flexDirection: 'column'
				}}
			>
				{/* Mobile Header */}
				<Box
					sx={{
						display: { xs: 'block', md: 'none' },
						position: 'sticky',
						top: 0,
						zIndex: 1000,
						backgroundColor: 'rgba(17, 15, 50, 0.95)',
						backdropFilter: 'blur(10px)',
						borderBottom: '1px solid rgba(75, 63, 215, 0.2)',
						py: 2,
						px: 2
					}}
				>
					<Stack
						direction="row"
						alignItems="center"
						justifyContent="space-between"
					>
						<Stack
							sx={{
								flexDirection: 'column',
								alignItems: 'flex-start',
								textAlign: 'left',
								gap: 0.5
							}}
						>
							<Typography
								sx={{
									fontSize: '1.2rem',
									color: '#FFF',
									fontWeight: 700
								}}
							>
								Video Stabilizer
							</Typography>
							<Typography
								sx={{
									fontSize: '0.7rem',
									color: '#4B3FD7',
									background: '#FFF',
									borderRadius: '4px',
									px: 1.5,
									py: 0.25
								}}
							>
								Powered by OpenCV & AI
							</Typography>
						</Stack>
						
						<Box
							onClick={handleDrawerToggle}
							sx={{
								cursor: 'pointer',
								p: 1,
								borderRadius: 1,
								'&:hover': {
									backgroundColor: 'rgba(75, 63, 215, 0.1)'
								}
							}}
						>
							<Box
								sx={{
									width: 24,
									height: 2,
									backgroundColor: '#FFF',
									margin: '4px 0',
									transition: '0.3s',
									'&:nth-of-type(1)': {
										transform: drawerOpen ? 'rotate(-45deg) translate(-5px, 6px)' : 'none'
									},
									'&:nth-of-type(2)': {
										opacity: drawerOpen ? 0 : 1
									},
									'&:nth-of-type(3)': {
										transform: drawerOpen ? 'rotate(45deg) translate(-5px, -6px)' : 'none'
									}
								}}
							/>
							<Box
								sx={{
									width: 24,
									height: 2,
									backgroundColor: '#FFF',
									margin: '4px 0',
									transition: '0.3s'
								}}
							/>
							<Box
								sx={{
									width: 24,
									height: 2,
									backgroundColor: '#FFF',
									margin: '4px 0',
									transition: '0.3s'
								}}
							/>
						</Box>
					</Stack>
				</Box>

				{/* Page Content */}
				<Box
					sx={{
						flex: 1,
						width: '100%',
						overflow: 'hidden'
					}}
				>
					<Outlet />
				</Box>
			</Box>
		</Box>
	)
}

export default MainLayout