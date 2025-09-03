import { Box, Typography, Paper, Grid, Divider, Chip, Container } from '@mui/material'
import { Code, Api, VideoFile } from '@mui/icons-material'

const Doc = () => {
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
					API Documentation
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
					Complete guide to the Video Stabilization API
				</Typography>

				<Grid container spacing={4}>
					<Grid item xs={12}>
						<Paper sx={{ 
							p: 4, 
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
							<Typography variant="h4" sx={{ color: '#4B3FD7', mb: 3, display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600 }}>
								<Api /> Endpoint: /stabilize-video
							</Typography>
						
							<Box sx={{ mb: 3 }}>
								<Chip label="POST" color="primary" sx={{ mr: 2 }} />
								<Chip label="Multipart Form Data" color="secondary" />
							</Box>

							<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 2 }}>
								Description
							</Typography>
							<Typography variant="body1" sx={{ mb: 3 }}>
								Upload a video file to stabilize it using advanced computer vision algorithms. 
								The API supports various parameters for customization and can return either the stabilized video 
								or detailed statistics about the stabilization process.
							</Typography>

							<Divider sx={{ my: 3, backgroundColor: 'rgba(255,255,255,0.2)' }} />

							<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 2 }}>
								Request Parameters
							</Typography>
						
							<Grid container spacing={2} sx={{ mb: 3 }}>
								<Grid item xs={12} md={6}>
									<Paper sx={{ 
										p: 2, 
										backgroundColor: 'rgba(255,255,255,0.1)',
										border: '1px solid rgba(255,255,255,0.2)',
										borderRadius: '8px',
										boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
										transition: 'all 0.3s ease',
										'&:hover': {
											background: 'rgba(255,255,255,0.15)',
											border: '1px solid rgba(255,255,255,0.3)'
										}
									}}>
										<Typography variant="subtitle1" sx={{ color: '#4B3FD7', fontWeight: 'bold' }}>
											Form Data
										</Typography>
										<Typography variant="body2" sx={{ mt: 1, color: '#FFF' }}>
											<strong>video:</strong> Video file (MP4, AVI, MOV, etc.)
										</Typography>
									</Paper>
								</Grid>
								<Grid item xs={12} md={6}>
									<Paper sx={{ 
										p: 2, 
										backgroundColor: 'rgba(255,255,255,0.1)',
										border: '1px solid rgba(255,255,255,0.2)',
										borderRadius: '8px',
										boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
										transition: 'all 0.3s ease',
										'&:hover': {
											background: 'rgba(255,255,255,0.15)',
											border: '1px solid rgba(255,255,255,0.3)'
										}
									}}>
										<Typography variant="subtitle1" sx={{ color: '#4B3FD7', fontWeight: 'bold' }}>
											Query Parameters
										</Typography>
										<Typography variant="body2" sx={{ mt: 1, color: '#FFF' }}>
											<strong>filename:</strong> Use existing file in /input directory
										</Typography>
									</Paper>
								</Grid>
							</Grid>

							<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 2 }}>
								Optional Query Parameters
							</Typography>
						
							<Grid container spacing={2} sx={{ mb: 3 }}>
								<Grid item xs={12} md={4}>
									<Paper sx={{ 
										p: 2, 
										backgroundColor: 'rgba(255,255,255,0.1)',
										border: '1px solid rgba(255,255,255,0.2)',
										borderRadius: '8px',
										boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
										transition: 'all 0.3s ease',
										'&:hover': {
											background: 'rgba(255,255,255,0.15)',
											border: '1px solid rgba(255,255,255,0.3)'
										}
									}}>
										<Typography variant="subtitle2" sx={{ color: '#4B3FD7', fontWeight: 600 }}>
											window
										</Typography>
										<Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#FFF' }}>
											Smoothing window size (3-60, default: 10)
										</Typography>
									</Paper>
								</Grid>
								<Grid item xs={12} md={4}>
									<Paper sx={{ 
										p: 2, 
										backgroundColor: 'rgba(255,255,255,0.1)',
										border: '1px solid rgba(255,255,255,0.2)',
										borderRadius: '8px',
										boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
										transition: 'all 0.3s ease',
										'&:hover': {
											background: 'rgba(255,255,255,0.15)',
											border: '1px solid rgba(255,255,255,0.3)'
										}
									}}>
										<Typography variant="subtitle2" sx={{ color: '#4B3FD7', fontWeight: 600 }}>
											crop
										</Typography>
										<Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#FFF' }}>
											Border crop ratio (0-0.2, default: 0.04)
										</Typography>
									</Paper>
								</Grid>
								<Grid item xs={12} md={4}>
									<Paper sx={{ 
										p: 2, 
										backgroundColor: 'rgba(255,255,255,0.1)',
										border: '1px solid rgba(255,255,255,0.2)',
										borderRadius: '8px',
										boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
										transition: 'all 0.3s ease',
										'&:hover': {
											background: 'rgba(255,255,255,0.15)',
											border: '1px solid rgba(255,255,255,0.3)'
										}
									}}>
										<Typography variant="subtitle2" sx={{ color: '#4B3FD7', fontWeight: 600 }}>
											overlay
										</Typography>
										<Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#FFF' }}>
											Show features & camera path (1 or 0)
										</Typography>
									</Paper>
								</Grid>
								<Grid item xs={12} md={4}>
									<Paper sx={{ 
										p: 2, 
										backgroundColor: 'rgba(255,255,255,0.1)',
										border: '1px solid rgba(255,255,255,0.2)',
										borderRadius: '8px',
										boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
										transition: 'all 0.3s ease',
										'&:hover': {
											background: 'rgba(255,255,255,0.15)',
											border: '1px solid rgba(255,255,255,0.3)'
										}
									}}>
										<Typography variant="subtitle2" sx={{ color: '#4B3FD7', fontWeight: 600 }}>
											sbs
										</Typography>
										<Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#FFF' }}>
											Side-by-side comparison (1 or 0)
										</Typography>
									</Paper>
								</Grid>
								<Grid item xs={12} md={4}>
									<Paper sx={{ 
										p: 2, 
										backgroundColor: 'rgba(255,255,255,0.9)',
										border: 'none',
										borderRadius: '12px',
										boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
										transition: 'all 0.3s ease',
										'&:hover': {
											transform: 'translateY(-1px)',
											boxShadow: '0 4px 20px rgba(0,0,0,0.12)'
										}
									}}>
										<Typography variant="subtitle2" sx={{ color: '#4B3FD7', fontWeight: 600 }}>
											stats
										</Typography>
										<Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#666' }}>
											Include transform statistics (1 or 0)
										</Typography>
									</Paper>
								</Grid>
								<Grid item xs={12} md={4}>
									<Paper sx={{ 
										p: 2, 
										backgroundColor: 'rgba(255,255,255,0.9)',
										border: 'none',
										borderRadius: '12px',
										boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
										transition: 'all 0.3s ease',
										'&:hover': {
											transform: 'translateY(-1px)',
											boxShadow: '0 4px 20px rgba(0,0,0,0.12)'
										}
									}}>
										<Typography variant="subtitle2" sx={{ color: '#4B3FD7', fontWeight: 600 }}>
											json
										</Typography>
										<Typography variant="body2" sx={{ fontSize: '0.9rem', color: '#666' }}>
											Return JSON instead of video (1 or 0)
										</Typography>
									</Paper>
								</Grid>
							</Grid>

							<Divider sx={{ my: 3, backgroundColor: 'rgba(255,255,255,0.2)' }} />

							<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 2 }}>
								Response
							</Typography>
						
							<Grid container spacing={3}>
								<Grid item xs={12} md={6}>
									<Paper sx={{ p: 3, backgroundColor: 'rgba(255,255,255,0.05)' }}>
										<Typography variant="subtitle1" sx={{ color: '#4B3FD7', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
											<VideoFile /> Video Response (default)
										</Typography>
										<Typography variant="body2" sx={{ mb: 2 }}>
											Returns the stabilized video file with additional headers:
										</Typography>
										<Box component="pre" sx={{ 
											fontSize: '0.8rem', 
											backgroundColor: 'rgba(0,0,0,0.3)', 
											p: 2, 
											borderRadius: 1,
											overflow: 'auto'
										}}>
{`X-Input-Video: original_filename.mp4
X-Smooth-Window: 10
X-Crop-Ratio: 0.0400
X-Overlay: 0
X-SideBySide: 0
X-Frames: 150`}
										</Box>
									</Paper>
								</Grid>
								
								<Grid item xs={12} md={6}>
									<Paper sx={{ p: 3, backgroundColor: 'rgba(255,255,255,0.05)' }}>
										<Typography variant="subtitle1" sx={{ color: '#4B3FD7', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
											<Code /> JSON Response (?json=1)
										</Typography>
										<Typography variant="body2" sx={{ mb: 2 }}>
											Returns detailed statistics about the stabilization:
										</Typography>
										<Box component="pre" sx={{ 
											fontSize: '0.8rem', 
											backgroundColor: 'rgba(0,0,0,0.3)', 
											p: 2, 
											borderRadius: 1,
											overflow: 'auto'
										}}>
{`{
  "video": "input.mp4",
  "output": "stabilized_input.mp4",
  "frames": 150,
  "smooth_window": 10,
  "crop_ratio": 0.04,
  "overlay": false,
  "side_by_side": false,
  "transforms": [...]
}`}
										</Box>
									</Paper>
								</Grid>
							</Grid>

							<Divider sx={{ my: 3, backgroundColor: 'rgba(255,255,255,0.2)' }} />

							<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 2 }}>
								Example Usage
							</Typography>
							
							<Paper sx={{ p: 3, backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 1 }}>
								<Typography variant="subtitle2" sx={{ color: '#4B3FD7', mb: 2 }}>
									JavaScript/React Example:
								</Typography>
								<Box component="pre" sx={{ 
									fontSize: '0.8rem', 
									color: '#FFF',
									overflow: 'auto'
								}}>
{`const formData = new FormData();
formData.append('video', videoFile);

const response = await fetch(
  'http://localhost:5000/stabilize-video?window=15&crop=0.05&overlay=1', 
  { method: 'POST', body: formData }
);

const stabilizedVideo = await response.blob();
const videoUrl = URL.createObjectURL(stabilizedVideo);`}
								</Box>
							</Paper>
						</Paper>
					</Grid>
				</Grid>
			</Box>
		</Container>
	)
}

export default Doc
