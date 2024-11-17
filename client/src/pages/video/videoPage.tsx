import React, { useState, useRef } from 'react'
import { Box, Button, Stack } from '@mui/material'

const VideoPage = () => {
	const [videoSrc, setVideoSrc] = useState<string | null>(null)
	const [showReplay, setShowReplay] = useState(false)
	const videoRef = useRef<HTMLVideoElement>(null)
	const [isLoadingClip, setIsLoadingClip] = useState(false)
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

				const blob = await response.blob()
				const videoURL = URL.createObjectURL(blob)
				console.log('videoURL:', videoURL)
				setIsLoadingClip(false)
				setVideoSrc(videoURL)
				setShowReplay(false)
			} catch (error) {
				console.error('Error uploading video:', error)
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
		</Box>
	)
}

export default VideoPage
