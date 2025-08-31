import React, { useState, useRef } from 'react'
import { Box, Button, Stack } from '@mui/material'

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
	const [stabilize, setStabilize] = useState(false)
	const [overlay, setOverlay] = useState(false)
	const [sideBySide, setSideBySide] = useState(false)
	const [windowSize, setWindowSize] = useState(10)
	const [cropRatio, setCropRatio] = useState(0.04)
	const [stats, setStats] = useState<Stats | null>(null)

	const handleVideoUpload = async (
		event: React.ChangeEvent<HTMLInputElement>
	) => {
		const file = event.target.files?.[0]
		if (file) {
			const formData = new FormData()
			formData.append('video', file)

			try {
				setIsLoadingClip(true)
				const params = new URLSearchParams()
				params.set('window', String(windowSize))
				params.set('crop', String(cropRatio))
				if (overlay) params.set('overlay', '1')
				if (sideBySide) params.set('sbs', '1')
				// Always request stats JSON in parallel
				const videoResp = await fetch('http://127.0.0.1:5000/stabilize-video?' + params.toString(), { method: 'POST', body: formData })
				const blob = await videoResp.blob()
				const videoURL = URL.createObjectURL(blob)
				// Fetch JSON stats
				params.set('json', '1')
				const jsonResp = await fetch('http://127.0.0.1:5000/stabilize-video?' + params.toString(), { method: 'POST', body: formData })
				let jsonData: any = null
				try { jsonData = await jsonResp.json(); } catch { jsonData = null }
				setStats(jsonData)
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
				<input type="checkbox" checked={stabilize} onChange={() => setStabilize(!stabilize)} />
				<span>Stabilize Video</span>
				<input type="checkbox" checked={overlay} onChange={() => setOverlay(!overlay)} />
				<span>Overlay features</span>
				<input type="checkbox" checked={sideBySide} onChange={() => setSideBySide(!sideBySide)} />
				<span>Side-by-side</span>
				<label style={{display:'flex',alignItems:'center',gap:4}}>Win
					<input style={{width:60}} type='number' value={windowSize} min={3} max={60} onChange={e=>setWindowSize(Number(e.target.value))} />
				</label>
				<label style={{display:'flex',alignItems:'center',gap:4}}>Crop
					<input style={{width:60}} type='number' step='0.01' value={cropRatio} min={0} max={0.2} onChange={e=>setCropRatio(Number(e.target.value))} />
				</label>
				<label htmlFor='video-upload'>
					<Button variant='contained' color='primary' component='span'>Upload Video</Button>
				</label>
				{stats && <Button variant='outlined' onClick={()=>setStats(null)}>Hide Stats</Button>}
			</Stack>
			{stats && (
				<Box sx={{mt:2, maxWidth:600, textAlign:'left', fontSize:12}}>
					<p>Frames: {stats.frames} | Window: {stats.smooth_window} | Crop: {stats.crop_ratio}</p>
					{stats.transforms && stats.transforms.length>0 && (
						<p>Last diff: dx ~ {Number(stats.transforms.at(-1).dx).toFixed(1)}, dy ~ {Number(stats.transforms.at(-1).dy).toFixed(1)}, ang ~ {(Number(stats.transforms.at(-1).da)*180/Math.PI).toFixed(2)}°</p>
					)}
				</Box>
			)}
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
