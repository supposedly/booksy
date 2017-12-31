import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { MediaItem } from '../classes';
import { MediaService } from '../media.service';


@Component({
  selector: 'app-media-info',
  templateUrl: './media-info.component.html',
  styleUrls: ['./media-info.component.css']
})
export class MediaInfoComponent implements OnInit {
  item: MediaItem;
  
  @Input() mID: number;
  
  constructor(
    private route: ActivatedRoute,
    private mediaService: MediaService,
    private location: Location
  ) { }
  
  ngOnInit(): void {
  }
  
  getItem(): void {
    this.mediaService.getInfo(this.mID)
      .subscribe(item => this.item = item);
  }

}
