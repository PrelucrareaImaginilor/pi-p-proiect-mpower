import { useState, useRef } from 'react'
import { 
	Box, 
	Button, 
	Stack, 
	Typography, 
	Paper, 
	FormControlLabel, 
	Checkbox, 
	Slider,
	CircularProgress,
	Alert,
	Card,
	CardContent,
	Grid,
	Container
} from '@mui/material'
import { 
	Upload, 
	PlayArrow, 
	Settings, 
	Analytics, 
	VideoLibrary 
} from '@mui/icons-material'

interface Transform {
	dx: number
	dy: number
	da: number
}

interface Stats {
	frames: number
	smooth_window: number
	crop_ratio: number
	transforms?: Transform[]
}

const VideoPage = () => {
	const [videoSrc, setVideoSrc] = useState<string | null>(null)
	const [showReplay, setShowReplay] = useState(false)
	const videoRef = useRef<HTMLVideoElement>(null)
	const [isLoadingClip, setIsLoadingClip] = useState(false)
	const [overlay, setOverlay] = useState(false)
	const [sideBySide, setSideBySide] = useState(false)
	const [windowSize, setWindowSize] = useState(10)
	const [cropRatio, setCropRatio] = useState(0.04)
	const [stats, setStats] = useState<Stats | null>(null)
	const [error, setError] = useState<string | null>(null)

	const handleVideoUpload = async (
		event: React.ChangeEvent<HTMLInputElement>
	) => {
		const file = event.target.files?.[0]
		if (file) {
			const formData = new FormData()
			formData.append('video', file)

			try {
				setIsLoadingClip(true)
				setError(null)
				const params = new URLSearchParams()
				params.set('window', String(windowSize))
				params.set('crop', String(cropRatio))
				params.set('format', 'mp4')
				// use faster estimation by default
				params.set('scale', '0.5')
				if (overlay) params.set('overlay', '1')
				if (sideBySide) params.set('sbs', '1')
				// also ask server to compute stats alongside video
				params.set('stats', '1')
				
				const videoResp = await fetch('http://127.0.0.1:5000/stabilize-video?' + params.toString(), { method: 'POST', body: formData })
				
				if (!videoResp.ok) {
					throw new Error(`Server error: ${videoResp.status}`)
				}
				
				const blob = await videoResp.blob()
				const videoURL = URL.createObjectURL(blob)
				setVideoSrc(videoURL)
				// Force reload the video element to display immediately
				if (videoRef.current) {
					videoRef.current.pause()
					videoRef.current.src = videoURL
					videoRef.current.load()
				}

				// Read output filename from response headers to fetch stats
				const outputName = videoResp.headers.get('X-Output-Video')
				if (outputName) {
					try {
						const statsResp = await fetch('http://127.0.0.1:5000/stats?output=' + encodeURIComponent(outputName))
						if (statsResp.ok) {
							const statsJson = await statsResp.json()
							// Normalize to Stats shape
							setStats({
								frames: statsJson.frames ?? 0,
								smooth_window: windowSize,
								crop_ratio: cropRatio,
								transforms: statsJson.transforms ?? []
							})
						}
					} catch {
						// ignore stats failure
					}
				}

				setIsLoadingClip(false)
				setShowReplay(false)
			} catch (error) {
				console.error('Error uploading video:', error)
				setError(error instanceof Error ? error.message : 'An error occurred')
				setIsLoadingClip(false)
			}
		}
	}

	const handleVideoEnd = () => {
		setShowReplay(true)
	}

	const handleReplay = () => {
		if (videoRef.current) {
			videoRef.current.currentTime = 0
			videoRef.current.play()
			setShowReplay(false)
		}
	}

	return (
		<Container maxWidth="lg" sx={{ py: 4 }}>
			<Box sx={{
				display: 'flex',
				flexDirection: 'column',
				width: '100%',
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
					Video Stabilization
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
					Upload your video and apply professional stabilization
				</Typography>

				{error && (
					<Alert severity="error" sx={{ width: '100%', maxWidth: 600 }}>
						{error}
					</Alert>
				)}

				<Paper sx={{ 
					p: 4, 
					backgroundColor: 'rgba(75, 63, 215, 0.1)', 
					color: '#FFF',
					width: '100%',
					maxWidth: 800,
					border: '1px solid rgba(75, 63, 215, 0.3)',
					borderRadius: '12px',
					boxShadow: 'none',
					transition: 'all 0.3s ease',
					'&:hover': {
						background: 'rgba(75, 63, 215, 0.2)',
						border: '1px solid rgba(75, 63, 215, 0.5)'
					}
				}}>
					<Typography variant="h5" sx={{ color: '#4B3FD7', mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
						<Settings /> Stabilization Settings
					</Typography>

					<Grid container spacing={3} sx={{ mb: 4 }}>
						<Grid item xs={12} md={6}>
							<Typography variant="subtitle1" sx={{ mb: 2, color: '#CCC' }}>
								Smoothing Window: {windowSize}
							</Typography>
							<Slider
								value={windowSize}
								onChange={(_, value) => setWindowSize(value as number)}
								min={3}
								max={60}
								marks={[
									{ value: 3, label: '3' },
									{ value: 10, label: '10' },
									{ value: 30, label: '30' },
									{ value: 60, label: '60' }
								]}
								sx={{
									'& .MuiSlider-thumb': { backgroundColor: '#4B3FD7' },
									'& .MuiSlider-track': { backgroundColor: '#4B3FD7' },
									'& .MuiSlider-rail': { backgroundColor: 'rgba(255,255,255,0.3)' }
								}}
							/>
							<Typography variant="caption" sx={{ color: '#999' }}>
								Higher values = smoother but slower stabilization
							</Typography>
						</Grid>

						<Grid item xs={12} md={6}>
							<Typography variant="subtitle1" sx={{ mb: 2, color: '#CCC' }}>
								Crop Ratio: {(cropRatio * 100).toFixed(1)}%
							</Typography>
							<Slider
								value={cropRatio}
								onChange={(_, value) => setCropRatio(value as number)}
								min={0}
								max={0.2}
								step={0.01}
								marks={[
									{ value: 0, label: '0%' },
									{ value: 0.04, label: '4%' },
									{ value: 0.1, label: '10%' },
									{ value: 0.2, label: '20%' }
								]}
								sx={{
									'& .MuiSlider-thumb': { backgroundColor: '#4B3FD7' },
									'& .MuiSlider-track': { backgroundColor: '#4B3FD7' },
									'& .MuiSlider-rail': { backgroundColor: 'rgba(255,255,255,0.3)' }
								}}
							/>
							<Typography variant="caption" sx={{ color: '#999' }}>
								Higher values hide more warping edges
							</Typography>
						</Grid>
					</Grid>

					<Stack direction="row" spacing={2} sx={{ mb: 4, flexWrap: 'wrap', gap: 2 }}>
						<FormControlLabel
							control={
								<Checkbox 
									checked={overlay} 
									onChange={(e) => setOverlay(e.target.checked)}
									sx={{ color: '#4B3FD7' }}
								/>
							}
							label="Show Features & Camera Path"
							sx={{ color: '#1a1a1a' }}
						/>
						<FormControlLabel
							control={
								<Checkbox 
									checked={sideBySide} 
									onChange={(e) => setSideBySide(e.target.checked)}
									sx={{ color: '#4B3FD7' }}
								/>
							}
							label="Side-by-Side Comparison"
							sx={{ color: '#1a1a1a' }}
						/>
					</Stack>

					<Box sx={{ textAlign: 'center' }}>
						<input
							accept='video/*'
							style={{ display: 'none' }}
							id='video-upload'
							type='file'
							onChange={handleVideoUpload}
						/>
						<label htmlFor='video-upload'>
							<Button 
								variant='contained' 
								size='large'
								component='span'
								startIcon={<Upload />}
								sx={{ 
									backgroundColor: '#4B3FD7',
									'&:hover': { backgroundColor: '#3B2FC7' },
									px: 4,
									py: 1.5
								}}
							>
								Upload Video
							</Button>
						</label>
					</Box>
				</Paper>

				{isLoadingClip && (
					<Paper sx={{ 
						p: 4, 
													backgroundColor: 'rgba(255,255,255,0.1)', 
							color: '#FFF',
							textAlign: 'center',
							minWidth: 300,
							border: '1px solid rgba(255,255,255,0.2)',
							borderRadius: '12px',
							boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
							transition: 'all 0.3s ease',
							'&:hover': {
								background: 'rgba(255,255,255,0.15)',
								border: '1px solid rgba(255,255,255,0.3)'
							}
					}}>
						<CircularProgress sx={{ color: '#4B3FD7', mb: 2 }} />
						<Typography variant="h6">Processing Video...</Typography>
						<Typography variant="body2" sx={{ color: '#FFF', mt: 1 }}>
							This may take a few minutes depending on video length
						</Typography>
					</Paper>
				)}

				{stats && (
					<Paper sx={{ 
						p: 3, 
						backgroundColor: 'rgba(255,255,255,0.1)', 
						color: '#FFF',
						width: '100%',
						maxWidth: 800,
						border: '1px solid rgba(255,255,255,0.2)',
						borderRadius: '12px',
						boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
						transition: 'all 0.3s ease',
						'&:hover': {
							background: 'rgba(255,255,255,0.15)',
							border: '1px solid rgba(255,255,255,0.3)'
						}
					}}>
						<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
							<Analytics /> Stabilization Statistics
						</Typography>
					
						<Grid container spacing={2}>
							<Grid item xs={12} md={4}>
								<Card sx={{ backgroundColor: 'rgba(255,255,255,0.05)' }}>
									<CardContent sx={{ textAlign: 'center' }}>
										<Typography variant="h4" sx={{ color: '#4B3FD7' }}>
											{stats.frames}
										</Typography>
										<Typography variant="body2">Total Frames</Typography>
									</CardContent>
								</Card>
							</Grid>
							<Grid item xs={12} md={4}>
								<Card sx={{ backgroundColor: 'rgba(255,255,255,0.05)' }}>
									<CardContent sx={{ textAlign: 'center' }}>
										<Typography variant="h4" sx={{ color: '#4B3FD7' }}>
											{stats.smooth_window}
										</Typography>
										<Typography variant="body2">Smoothing Window</Typography>
									</CardContent>
								</Card>
							</Grid>
							<Grid item xs={12} md={4}>
								<Card sx={{ backgroundColor: 'rgba(255,255,255,0.05)' }}>
									<CardContent sx={{ textAlign: 'center' }}>
										<Typography variant="h4" sx={{ color: '#4B3FD7' }}>
											{(stats.crop_ratio * 100).toFixed(1)}%
										</Typography>
										<Typography variant="body2">Crop Ratio</Typography>
									</CardContent>
								</Card>
							</Grid>
						</Grid>

						{stats.transforms && stats.transforms.length > 0 && (
							<Box sx={{ mt: 3, p: 2, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 1 }}>
								<Typography variant="subtitle2" sx={{ color: '#4B3FD7', mb: 1 }}>
									Last Frame Transform:
								</Typography>
								<Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
									dx: {Number(stats.transforms[stats.transforms.length - 1]?.dx).toFixed(2)} | 
									dy: {Number(stats.transforms[stats.transforms.length - 1]?.dy).toFixed(2)} | 
									angle: {(Number(stats.transforms[stats.transforms.length - 1]?.da) * 180 / Math.PI).toFixed(2)}°
								</Typography>
							</Box>
						)}

						<Box sx={{ textAlign: 'center', mt: 3 }}>
							<Button 
								variant='outlined' 
								onClick={() => setStats(null)}
								sx={{ color: '#4B3FD7', borderColor: '#4B3FD7' }}
							>
								Hide Statistics
							</Button>
						</Box>
					</Paper>
				)}

				{videoSrc && (
					<Paper sx={{ 
						p: 3, 
						backgroundColor: 'rgba(255,255,255,0.15)', 
						color: '#FFF',
						width: '100%',
						maxWidth: 800,
						textAlign: 'center',
						border: '1px solid rgba(255,255,255,0.2)',
						boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
					}}>
						<Typography variant="h6" sx={{ color: '#4B3FD7', mb: 3, display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
							<VideoLibrary /> Stabilized Video
						</Typography>
						
						<video
							ref={videoRef}
							width='100%'
							controls
							onEnded={handleVideoEnd}
							style={{ borderRadius: '8px', maxWidth: '600px' }}
							src={videoSrc}
						>
							Your browser does not support the video tag.
						</video>

						{showReplay && (
							<Button
								variant='contained'
								startIcon={<PlayArrow />}
								onClick={handleReplay}
								sx={{ 
									backgroundColor: '#4B3FD7',
									'&:hover': { backgroundColor: '#3B2FC7' },
									mt: 2
								}}
							>
								Replay
							</Button>
						)}
					</Paper>
				)}
			</Box>
		</Container>
	)
}

export default VideoPage
