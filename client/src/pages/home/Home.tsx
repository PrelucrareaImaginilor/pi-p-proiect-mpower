import { Box, Typography, Button, Paper, Grid, Container } from '@mui/material'
import { useNavigate } from 'react-router-dom'

const Home = () => {
	const navigate = useNavigate()

	return (
		<Container maxWidth="lg" sx={{ py: 4 }}>
			<Box sx={{ 
				display: 'flex', 
				flexDirection: 'column', 
				alignItems: 'center', 
				justifyContent: 'center',
				minHeight: '60vh',
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
					Professional Video Stabilization
				</Typography>
				
				<Typography 
					variant="h6" 
					sx={{ 
						color: '#4B3FD7', 
						textAlign: 'center', 
						mb: 4, 
						maxWidth: 600,
						fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' }
					}}
				>
					Transform shaky videos into smooth, professional content using advanced computer vision algorithms
				</Typography>

				<Button 
					variant="contained" 
					size="large" 
					onClick={() => navigate('/video')}
					sx={{ 
						backgroundColor: '#4B3FD7', 
						'&:hover': { backgroundColor: '#3B2FC7' },
						px: 4,
						py: 2,
						fontSize: { xs: '1rem', sm: '1.1rem', md: '1.2rem' }
					}}
				>
					Start Stabilizing
				</Button>

				<Grid container spacing={3} sx={{ maxWidth: 1000, mt: 4 }}>
					<Grid item xs={12} sm={6} md={4}>
						<Paper sx={{ 
							p: 3, 
							textAlign: 'center', 
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
							<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 2, fontWeight: 700, fontSize: '1.1rem' }}>
								Smart Stabilization
							</Typography>
							<Typography variant="body2" sx={{ color: '#FFF', lineHeight: 1.6, fontSize: '0.95rem' }}>
								Advanced optical flow algorithms detect and compensate for camera movement
							</Typography>
						</Paper>
					</Grid>
					
					<Grid item xs={12} sm={6} md={4}>
						<Paper sx={{ 
							p: 3, 
							textAlign: 'center', 
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
							<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 2, fontWeight: 700, fontSize: '1.1rem' }}>
								Customizable Settings
							</Typography>
							<Typography variant="body2" sx={{ color: '#FFF', lineHeight: 1.6, fontSize: '0.95rem' }}>
								Adjust smoothing windows, crop ratios, and overlay features for optimal results
							</Typography>
						</Paper>
					</Grid>
					
					<Grid item xs={12} sm={6} md={4}>
						<Paper sx={{ 
							p: 3, 
							textAlign: 'center', 
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
							<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 2, fontWeight: 700, fontSize: '1.1rem' }}>
								Real-time Analysis
							</Typography>
							<Typography variant="body2" sx={{ color: '#FFF', lineHeight: 1.6, fontSize: '0.95rem' }}>
								View detailed transform statistics and camera path visualization
							</Typography>
						</Paper>
					</Grid>
				</Grid>

				<Typography 
					variant="body1" 
					sx={{ 
						color: '#CCC', 
						textAlign: 'center', 
						mt: 4, 
						maxWidth: 600,
						fontSize: { xs: '0.9rem', sm: '1rem' }
					}}
				>
					Perfect for content creators, filmmakers, and anyone looking to improve video quality. 
					Upload your video and get professional-grade stabilization in minutes.
				</Typography>
			</Box>
		</Container>
	)
}

export default Home
