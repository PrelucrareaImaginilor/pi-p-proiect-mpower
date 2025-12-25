import { Box, Typography, Paper, Grid, List, ListItem, ListItemText, ListItemIcon, Container } from '@mui/material'
import { Settings, VideoLibrary, Analytics, Crop, Timeline, Visibility } from '@mui/icons-material'

const Legend = () => {
	return (
		<Container maxWidth="lg" sx={{ py: 4 }}>
			<Box sx={{ 
				display: 'flex', 
				flexDirection: 'column', 
				alignItems: 'center', 
				gap: 4
			}}>
				<Typography 
					variant="h3" 
					sx={{ 
						color: '#FFF', 
						textAlign: 'center', 
						mb: 2,
						fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' }
					}}
				>
					Video Stabilization Features
				</Typography>
				
				<Typography 
					variant="h6" 
					sx={{ 
						color: '#4B3FD7', 
						textAlign: 'center', 
						mb: 4,
						fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' }
					}}
				>
					Advanced computer vision algorithms for professional video stabilization
				</Typography>

				<Grid container spacing={4}>
					<Grid item xs={12} md={6}>
						<Paper sx={{ 
							p: 3, 
							backgroundColor: 'rgba(75, 63, 215, 0.1)', 
							color: '#FFF', 
							height: '100%',
							border: '1px solid rgba(75, 63, 215, 0.3)',
							borderRadius: '12px',
							boxShadow: 'none',
							transition: 'all 0.3s ease',
							'&:hover': {
								background: 'rgba(75, 63, 215, 0.2)',
								border: '1px solid rgba(75, 63, 215, 0.5)'
							}
						}}>
							<Typography variant="h5" sx={{ color: '#4B3FD7', mb: 3, display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600 }}>
								<VideoLibrary /> Core Technology
							</Typography>
							<List>
								<ListItem>
									<ListItemIcon sx={{ color: '#4B3FD7' }}>
										<Analytics />
									</ListItemIcon>
									<ListItemText 
										primary="Optical Flow Detection" 
										secondary="Uses Lucas-Kanade algorithm to track feature points between frames"
									/>
								</ListItem>
								<ListItem>
									<ListItemIcon sx={{ color: '#4B3FD7' }}>
										<Timeline />
									</ListItemIcon>
									<ListItemText 
										primary="Affine Transform Estimation" 
										secondary="RANSAC-based robust estimation of camera movement"
									/>
								</ListItem>
								<ListItem>
									<ListItemIcon sx={{ color: '#4B3FD7' }}>
										<Settings />
									</ListItemIcon>
									<ListItemText 
										primary="Moving Average Smoothing" 
										secondary="Configurable window size for optimal stabilization"
									/>
								</ListItem>
							</List>
						</Paper>
					</Grid>

					<Grid item xs={12} md={6}>
						<Paper sx={{ 
							p: 3, 
							backgroundColor: 'rgba(255,255,255,0.1)', 
							color: '#FFF', 
							height: '100%',
							border: '1px solid rgba(255,255,255,0.2)',
							borderRadius: '12px',
							boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
							transition: 'all 0.3s ease',
							'&:hover': {
								background: 'rgba(255,255,255,0.15)',
								border: '1px solid rgba(255,255,255,0.3)'
							}
						}}>
							<Typography variant="h5" sx={{ color: '#4B3FD7', mb: 3, display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600 }}>
								<Settings /> Adjustable Parameters
							</Typography>
							<List>
								<ListItem>
									<ListItemIcon sx={{ color: '#4B3FD7' }}>
										<Timeline />
									</ListItemIcon>
									<ListItemText 
										primary="Smoothing Window" 
										secondary="Number of frames for moving average (3-60, default: 10)"
									/>
								</ListItem>
								<ListItem>
									<ListItemIcon sx={{ color: '#4B3FD7' }}>
										<Crop />
									</ListItemIcon>
									<ListItemText 
										primary="Crop Ratio" 
										secondary="Border crop to hide warping edges (0-0.2, default: 0.04)"
									/>
								</ListItem>
								<ListItem>
									<ListItemIcon sx={{ color: '#4B3FD7' }}>
										<Visibility />
									</ListItemIcon>
									<ListItemText 
										primary="Feature Overlay" 
										secondary="Visualize tracked features and camera path"
									/>
								</ListItem>
							</List>
						</Paper>
					</Grid>

					<Grid item xs={12}>
						<Paper sx={{ 
							p: 3, 
							backgroundColor: 'rgba(255,255,255,0.1)', 
							color: '#FFF',
							border: '1px solid rgba(255,255,255,0.2)',
							borderRadius: '12px',
							boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
							transition: 'all 0.3s ease',
							'&:hover': {
								background: 'rgba(255,255,255,0.15)',
								border: '1px solid rgba(255,255,255,0.3)'
							}
						}}>
							<Typography variant="h5" sx={{ color: '#4B3FD7', mb: 3, textAlign: 'center', fontWeight: 600 }}>
								How It Works
							</Typography>
							<Grid container spacing={2}>
								<Grid item xs={12} md={3}>
									<Box sx={{ textAlign: 'center', p: 2 }}>
										<Typography variant="h6" sx={{ color: '#4B3FD7' }}>1. Feature Detection</Typography>
										<Typography variant="body2">Detect up to 500 feature points using Shi-Tomasi corner detection</Typography>
									</Box>
								</Grid>
								<Grid item xs={12} md={3}>
									<Box sx={{ textAlign: 'center', p: 2 }}>
										<Typography variant="h6" sx={{ color: '#4B3FD7' }}>2. Motion Tracking</Typography>
										<Typography variant="body2">Track features between consecutive frames using optical flow</Typography>
									</Box>
								</Grid>
								<Grid item xs={12} md={3}>
									<Box sx={{ textAlign: 'center', p: 2 }}>
										<Typography variant="h6" sx={{ color: '#4B3FD7' }}>3. Transform Estimation</Typography>
										<Typography variant="body2">Calculate affine transformation matrix using RANSAC</Typography>
									</Box>
								</Grid>
								<Grid item xs={12} md={3}>
									<Box sx={{ textAlign: 'center', p: 2 }}>
										<Typography variant="h6" sx={{ color: '#4B3FD7' }}>4. Stabilization</Typography>
										<Typography variant="body2">Apply smoothed transforms to create stable output</Typography>
									</Box>
								</Grid>
							</Grid>
						</Paper>
					</Grid>
				</Grid>
			</Box>
		</Container>
	)
}

export default Legend
