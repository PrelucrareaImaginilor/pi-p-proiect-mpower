import React, { useState, useRef } from 'react'
import { Box, Button, Stack, Typography } from '@mui/material'
interface VehicleStats {
	id: number
	max_speed: number
	avg_speed: number
}
const VideoPage = () => {
	const [videoSrc, setVideoSrc] = useState<string | null>(null)
	const [showReplay, setShowReplay] = useState(false)
	const videoRef = useRef<HTMLVideoElement>(null)
	const [isLoadingClip, setIsLoadingClip] = useState(false)
	const [carsData, setCarsData] = useState<VehicleStats[]>([])
	const handleVideoUpload = async (
		event: React.ChangeEvent<HTMLInputElement>
	) => {
		const file = event.target.files?.[0]
		if (file) {
			const formData = new FormData()
			formData.append('video', file)

			try {
				setIsLoadingClip(true)
				const response = await fetch(
					'http://127.0.0.1:5000/process-video',
					{
						method: 'POST',
						body: formData,
					}
				)

				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`)
				}

				const vehicleStats = response.headers.get('X-Vehicle-Stats')
				console.log('Raw headers:', response.headers)
				console.log('Vehicle stats:', vehicleStats)

				if (vehicleStats) {
					const stats = JSON.parse(vehicleStats)
					setCarsData(stats)
				}

				const blob = await response.blob()
				const videoURL = URL.createObjectURL(blob)
				setVideoSrc(videoURL)
				setShowReplay(false)
			} catch (error) {
				console.error('Error:', error)
			} finally {
				setIsLoadingClip(false)
			}
		}
	}
	console.log(carsData)
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
		<Box
			sx={{
				display: 'flex',
				flexDirection: 'column',
				width: '100%',
				alignItems: 'center',
				height: 'fit-content',
			}}
		>
			<input
				accept='video/*'
				style={{ display: 'none' }}
				id='video-upload'
				type='file'
				onChange={handleVideoUpload}
			/>

			<Stack
				sx={{
					flexDirection: 'row',
					width: 'fit-content',
					alignItems: 'center',
					gap: 2,
				}}
			>
				<label htmlFor='video-upload'>
					<Button
						variant='contained'
						color='primary'
						component='span'
					>
						Upload Video
					</Button>
				</label>
				{showReplay && (
					<Button
						variant='contained'
						color='secondary'
						onClick={handleReplay}
						sx={{
							width: 'fit-content',
						}}
					>
						Replay
					</Button>
				)}
				{videoSrc && (
					<Button
						onClick={() => setVideoSrc(null)}
						sx={{
							width: 'fit-content',
							color: 'red',
							'&:hover': {
								backgroundColor: 'red',
								color: 'white',
							},
						}}
					>
						Delete Video
					</Button>
				)}
			</Stack>

			{videoSrc && (
				<Box mt={2}>
					<video
						ref={videoRef}
						width='600'
						controls
						onEnded={handleVideoEnd}
					>
						<source src={videoSrc} type='video/mp4' />
						Your browser does not support the video tag.
					</video>
				</Box>
			)}
			{isLoadingClip && <p>Loading...</p>}
			<Box
				sx={{
					width: '80%',
				}}
			></Box>
			{carsData.length > 0 && (
				<Box
					sx={{
						width: '1200px',
						display: 'grid',
						height: '400px',
						overflowY: 'auto',
						gridTemplateColumns: 'repeat(3, 1fr)',
						gap: 2,
						mt: 3,
					}}
				>
					{carsData.map((car) => (
						<Box
							key={car.id}
							sx={{
								border: '1px solid #ccc',
								borderRadius: 1,
								p: 2,
								display: 'flex',
								justifyContent: 'space-between',
								alignItems: 'center',
								bgcolor: '#f5f5f5',
							}}
						>
							<Typography
								variant='body1'
								sx={{ fontWeight: 'bold' }}
							>
								ID: {car.id}
							</Typography>
							<Typography variant='body2' color='success'>
								Avg: {car.avg_speed.toFixed(1)} km/h
							</Typography>
							<Typography variant='body2' color='primary'>
								Max: {car.max_speed.toFixed(1)} km/h
							</Typography>
						</Box>
					))}
				</Box>
			)}
		</Box>
	)
}

export default VideoPage
