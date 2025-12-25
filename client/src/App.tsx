import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/home/Home'
import Legend from './pages/legend/Legend'
import MainLayout from './layouts/MainLayout'
import VideoPage from './pages/video/videoPage'
import Doc from './pages/doc/Doc'
import './App.css'

function App() {
	return (
		<Router>
			<Routes>
				<Route element={<MainLayout children={undefined} />}>
					<Route path='/' element={<Home />} />
					<Route path='/legend' element={<Legend />} />
					<Route path='/video' element={<VideoPage />} />
					<Route path='/docs' element={<Doc />} />
				</Route>
			</Routes>
		</Router>
	)
}

export default App
