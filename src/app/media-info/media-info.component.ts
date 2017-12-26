import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { MediaItem } from '../classes';
import { MediaService } '../media.service';


@Component({
  selector: 'app-media-info',
  templateUrl: './media-info.component.html',
  styleUrls: ['./media-info.component.css']
})
export class MediaInfoComponent implements OnInit {
  item: MediaItem;
  
  @Input() mid: number;
  
  constructor(
    private route: ActivatedRoute,
    private mediaService: MediaService,
    private location: Location
  ) { }
  
  ngOnInit(): void {
  }
  
  getItem(): void {
    this.mediaService.getInfo(mid)
      .subscribe(item => this.item = item);
  }

}
